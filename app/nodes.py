"""
Agent node functions for the LangGraph pipeline.

Each function takes the shared AppState and returns a dict of
updates to merge back into state. LangGraph handles the merging.
"""

import json
import re
from datetime import date
from typing import Any

from app.state import AppState
from app.llm import get_llm
from app.pdf import compile_latex, count_pdf_pages
from app.storage import get_resume
from app.prompts import (
    INTAKE_PROMPT,
    TAILOR_PROMPT,
    COVER_LETTER_PROMPT,
    EVALUATOR_PROMPT,
)


# ============================================================
# Helpers
# ============================================================

def _strip_code_fences(text: str) -> str:
    """
    LLMs sometimes wrap output in markdown code fences despite
    instructions not to. Strip them defensively.
    """
    text = text.strip()
    # Remove ```json ... ``` or ```latex ... ``` or ``` ... ```
    fence_pattern = r"^```(?:\w+)?\n(.*)\n```$"
    match = re.match(fence_pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text


def _parse_json_response(text: str) -> dict[str, Any]:
    """
    Parse an LLM response that should be JSON. Handles code fences
    and raises a clear error if the LLM broke the contract.
    """
    cleaned = _strip_code_fences(text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"LLM did not return valid JSON. Got:\n{cleaned[:500]}\nError: {e}"
        )

def _normalize_for_comparison(tex: str) -> str:
    """
    Strip parenthetical qualifiers and trailing role modifiers from
    job-title-like lines before sending to the evaluator. This prevents
    the evaluator from flagging trivial title shortenings as fabrication.

    Examples:
      "Senior Cloud Engineer (ML)"           → "Senior Cloud Engineer"
      "Software Engineer II, Payments Team"  → "Software Engineer II"
      "Staff SWE - Infrastructure"           → "Staff SWE"
    """
    # Remove parentheticals: "(anything)"
    tex = re.sub(r"\s*\([^)]*\)", "", tex)
    # Remove trailing ", team/role" or " - team/role" on a line
    tex = re.sub(r"(,|\s-\s)\s*[A-Za-z][\w\s&/]*$", "", tex, flags=re.MULTILINE)
    return tex

def _escape_unescaped_percent(tex: str) -> str:
    """
    Replace unescaped `%` with `\\%` in LaTeX body content.
    Skips `%` that is already escaped (preceded by a backslash).
    """
    return re.sub(r"(?<!\\)%", r"\\%", tex)


def _escape_cover_letter_specials(tex: str) -> str:
    """
    Escape LaTeX special characters that commonly appear in company names
    and JD titles but break compilation if unescaped.

    Handles: %, &
    Focuses on prose lines only — skips lines that start with a LaTeX
    command or a comment, so we don't break valid commands like \\&
    or valid table content.
    """
    lines = tex.split("\n")
    fixed_lines = []
    for line in lines:
        stripped = line.lstrip()
        # Skip LaTeX command lines and comment lines — they legitimately use these chars
        if stripped.startswith("\\") or stripped.startswith("%"):
            fixed_lines.append(line)
            continue
        # Escape unescaped %
        line = re.sub(r"(?<!\\)%", r"\\%", line)
        # Escape unescaped &
        line = re.sub(r"(?<!\\)&", r"\\&", line)
        fixed_lines.append(line)
    return "\n".join(fixed_lines)


# ============================================================
# Node 1: Intake
# ============================================================

def intake(state: AppState) -> dict:
    """
    Load the user's base resume from Supabase and parse the JD
    into structured analysis.

    Input:  state["user_id"], state["jd_text"]
    Output: {"base_resume": <loaded>, "jd_analysis": {role, skills, keywords, tone}}
    """
    # Load base resume from DB (unless already provided — Phase 1 compatibility)
    base_resume = state.get("base_resume")
    if not base_resume:
        base_resume = get_resume(state["user_id"])
        if not base_resume:
            raise ValueError(
                f"No base resume found for user {state['user_id']}. "
                f"Save one with save_resume() before running the graph."
            )

    llm = get_llm("fast")

    messages = [
        {"role": "system", "content": INTAKE_PROMPT},
        {"role": "user", "content": f"Job description:\n\n{state['jd_text']}"},
    ]

    response = llm.invoke(messages)
    analysis = _parse_json_response(response.content)

    required = {"role", "skills", "keywords", "tone"}
    missing = required - set(analysis.keys())
    if missing:
        raise ValueError(f"Intake LLM response missing keys: {missing}")

    return {
        "base_resume": base_resume,
        "jd_analysis": analysis,
    }

# ============================================================
# Node 2: Tailor Resume
# ============================================================

def tailor_resume(state: AppState) -> dict:
    """
    Rewrite the base resume to emphasize JD-relevant experience.
    Must not fabricate anything (Evaluator will catch violations).
    Enforces page-count constraint: output must not exceed base resume page count.

    Input:  state["base_resume"], state["jd_analysis"], optional state["user_feedback"]
    Output: {"tailored_resume_tex": str}
    """
    llm = get_llm("writer")

    # Compile the base resume once to get its true page count
    try:
        base_pdf = compile_latex(state["base_resume"])
        base_pages = count_pdf_pages(base_pdf)
    except Exception as e:
        raise RuntimeError(f"Base resume failed to compile: {e}")

    base_len = len(state["base_resume"])

    user_parts = [
        f"Base resume (LaTeX) — renders to {base_pages} page(s), {base_len} characters:\n\n{state['base_resume']}",
        f"JD analysis:\n\n{json.dumps(state['jd_analysis'], indent=2)}",
        (
            f"LENGTH CONSTRAINT: The tailored resume MUST render on {base_pages} page(s) or fewer. "
            f"The base resume is {base_len} characters. Aim for similar or shorter. "
            f"If a rephrasing makes a bullet longer, shorten another bullet to compensate. "
            f"Drop the least JD-relevant content if needed to fit."
        ),
    ]

    feedback = state.get("user_feedback")
    if feedback:
        user_parts.append(f"Revision feedback from user:\n{feedback}")

    messages = [
        {"role": "system", "content": TAILOR_PROMPT},
        {"role": "user", "content": "\n\n---\n\n".join(user_parts)},
    ]

    MAX_ATTEMPTS = 3
    last_tex = None

    for attempt in range(MAX_ATTEMPTS):
        response = llm.invoke(messages)
        tex = _strip_code_fences(response.content)
        last_tex = tex

        if "\\documentclass" not in tex or "\\end{document}" not in tex:
            raise ValueError(
                f"Tailor LLM did not return a complete LaTeX document (attempt {attempt + 1}). "
                f"First 200 chars:\n{tex[:200]}"
            )

        # Compile and count pages
        try:
            pdf = compile_latex(tex)
            pages = count_pdf_pages(pdf)
        except Exception as e:
            # If tailored LaTeX breaks, ask LLM to fix it
            messages.append({"role": "assistant", "content": tex})
            messages.append(
                {
                    "role": "user",
                    "content": (
                        f"Your output failed to compile with Tectonic:\n{str(e)[:500]}\n\n"
                        f"Regenerate a valid LaTeX resume. Output ONLY the LaTeX code."
                    ),
                }
            )
            continue

        print(f"  Attempt {attempt + 1}: {len(tex)} chars, {pages} page(s)")

        if pages <= base_pages:
            return {"tailored_resume_tex": tex}

        # Too many pages — ask for a shorter version
        messages.append({"role": "assistant", "content": tex})
        messages.append(
            {
                "role": "user",
                "content": (
                    f"Your previous output renders to {pages} pages, but the limit is {base_pages}. "
                    f"Regenerate the tailored resume, aggressively trimming to fit within {base_pages} page(s). "
                    f"Drop the least JD-relevant bullets entirely. Shorten verbose phrasing. "
                    f"Output ONLY the LaTeX code."
                ),
            }
        )

    print(
        f"WARNING: Tailor output still exceeds {base_pages} pages after {MAX_ATTEMPTS} attempts. "
        f"Proceeding with last attempt."
    )
    return {"tailored_resume_tex": last_tex}


# ============================================================
# Node 3: Cover Letter
# ============================================================

def cover_letter(state: AppState) -> dict:
    """
    Draft a cover letter grounded in the base resume and JD.
    Uses a clean article-based template; date is injected deterministically.

    Input:  state["base_resume"], state["jd_text"], state["jd_analysis"],
            optional state["user_feedback"]
    Output: {"cover_letter_tex": str}
    """
    llm = get_llm("writer")

    today_str = date.today().strftime("%B %d, %Y")
    date_sentinel = "__COVER_LETTER_DATE__"

    user_parts = [
        (
            f"DATE INSTRUCTION: wherever the template shows the date, "
            f"insert the literal token {date_sentinel} (exactly that, no substitution). "
            f"Do not output any actual date — we will replace the token after generation."
        ),
        f"Base resume (LaTeX) — extract name, city, email, phone from here:\n\n{state['base_resume']}",
        f"Job description:\n\n{state['jd_text']}",
        f"JD analysis:\n\n{json.dumps(state['jd_analysis'], indent=2)}",
    ]

    feedback = state.get("user_feedback")
    if feedback:
        user_parts.append(f"Revision feedback from user:\n{feedback}")

    messages = [
        {"role": "system", "content": COVER_LETTER_PROMPT},
        {"role": "user", "content": "\n\n---\n\n".join(user_parts)},
    ]

    response = llm.invoke(messages)
    tex = _strip_code_fences(response.content)

    # Sanity check: must look like a LaTeX document
    if "\\documentclass" not in tex or "\\end{document}" not in tex:
        raise ValueError(
            f"Cover letter LLM did not return a complete LaTeX document. "
            f"First 200 chars:\n{tex[:200]}"
        )

    # Deterministic date injection — replace sentinel (or fall back to any date-looking line we find)
    if date_sentinel in tex:
        tex = tex.replace(date_sentinel, today_str)
    else:
        print(f"WARNING: cover letter did not contain date sentinel; date may be wrong")

    # Defensive: catch leftover placeholders
    bad_placeholders = ["[Date]", "[Your Name]", "[Company Name]", "[Company]"]
    leftover = [p for p in bad_placeholders if p in tex]
    if leftover:
        print(f"WARNING: cover letter contains placeholders: {leftover}")

    tex = _escape_cover_letter_specials(tex)
    return {"cover_letter_tex": tex}

# ============================================================
# Node 4: Evaluator
# ============================================================

def evaluate(state: AppState) -> dict:
    """
    Audit the generated outputs. Reports divergence, ATS, tone, and
    a list of items added vs the base resume. Does NOT block on
    divergence — passing only depends on ATS and tone thresholds.

    Input:  state["base_resume"], state["tailored_resume_tex"],
            state["cover_letter_tex"], state["jd_analysis"]
    Output: {"eval_report": {...}, "retry_count": incremented}
    """
    llm = get_llm("fast")

    tailored = state.get("tailored_resume_tex") or "(not generated)"
    letter = state.get("cover_letter_tex") or "(not generated)"

    # Normalize both sides so the auditor doesn't flag synonym/rephrasing differences
    base_for_eval = _normalize_for_comparison(state["base_resume"])
    tailored_for_eval = (
        _normalize_for_comparison(tailored)
        if tailored != "(not generated)"
        else tailored
    )

    user_content = (
        f"BASE RESUME (ground truth):\n\n{base_for_eval}\n\n"
        f"---\n\n"
        f"TAILORED RESUME:\n\n{tailored_for_eval}\n\n"
        f"---\n\n"
        f"COVER LETTER:\n\n{letter}\n\n"
        f"---\n\n"
        f"JD ANALYSIS:\n\n{json.dumps(state['jd_analysis'], indent=2)}"
    )

    messages = [
        {"role": "system", "content": EVALUATOR_PROMPT},
        {"role": "user", "content": user_content},
    ]

    response = llm.invoke(messages)
    report = _parse_json_response(response.content)

    required = {"divergence_score", "ats_score", "tone_score", "passed", "added_items", "issues"}
    missing = required - set(report.keys())
    if missing:
        raise ValueError(f"Evaluator response missing keys: {missing}")

    # Clamp LLM-provided scores
    for key in ("divergence_score", "tone_score"):
        report[key] = max(0.0, min(1.0, float(report[key])))

    # Override ATS score with deterministic computation
    keywords = state["jd_analysis"].get("keywords", [])
    combined_text = (state.get("tailored_resume_tex") or "") + "\n" + (state.get("cover_letter_tex") or "")
    text_lower = combined_text.lower()
    matched_keywords = [kw for kw in keywords if kw.lower() in text_lower]
    missing_keywords = [kw for kw in keywords if kw.lower() not in text_lower]
    ats_score = len(matched_keywords) / len(keywords) if keywords else 1.0

    report["ats_score"] = ats_score
    report["matched_keywords"] = matched_keywords
    report["missing_keywords"] = missing_keywords

    # Ensure list types
    if not isinstance(report["issues"], list):
        report["issues"] = [str(report["issues"])]
    if not isinstance(report["added_items"], list):
        report["added_items"] = [str(report["added_items"])]

    # Add deterministic ATS issue if below threshold
    report["issues"] = [
        i for i in report["issues"]
        if "ats" not in i.lower() and "keyword" not in i.lower()
    ]
    if ats_score < 0.6:
        report["issues"].append(
            f"ATS coverage below minimum: {len(matched_keywords)}/{len(keywords)} "
            f"JD keywords matched ({ats_score:.0%}). Minimum is 60%."
        )

    # Compute `passed` deterministically — divergence is informational, does NOT block
    report["passed"] = (
        report["ats_score"] >= 0.6
        and report["tone_score"] >= 0.6
    )

    new_retry_count = state.get("retry_count", 0) + 1

    return {
        "eval_report": report,
        "retry_count": new_retry_count,
    }

# ============================================================
# Node 5: ATS Pre-Check
# ============================================================

def ats_precheck(state: AppState) -> dict:
    """
    Compute baseline ATS coverage of the base resume against the JD,
    before any tailoring. Surfaces the gap so the user can decide to
    improve their resume before spending tokens on generation.

    Input:  state["base_resume"], state["jd_analysis"]
    Output: {"ats_precheck": {baseline_score, matched_keywords, missing_keywords}}
    """
    keywords = state["jd_analysis"].get("keywords", [])
    base_resume_lower = state["base_resume"].lower()

    matched = [kw for kw in keywords if kw.lower() in base_resume_lower]
    missing = [kw for kw in keywords if kw.lower() not in base_resume_lower]

    baseline_score = len(matched) / len(keywords) if keywords else 1.0

    return {
        "ats_precheck": {
            "baseline_score": baseline_score,
            "matched_keywords": matched,
            "missing_keywords": missing,
        }
    }

# ============================================================
# Node 6: Human Approval
# ============================================================

def human_approval(state: AppState) -> dict:
    """
    Pass-through node that exists as an anchor for the interrupt.
    The graph pauses BEFORE this runs so the UI can show the user
    the evaluation results and collect a decision.

    When the graph resumes:
      - If user_decision == "revise", graph routing sends us back to tailor
      - Otherwise (approve, or no decision), this node runs and graph ends
    """
    # Nothing to do; the interrupt happens before this executes.
    # We just return an empty dict to keep state unchanged.
    return {}
