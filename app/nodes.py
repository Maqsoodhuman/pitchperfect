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
    

# ============================================================
# Node 1: Intake
# ============================================================

def intake(state: AppState) -> dict:
    """
    Parse the JD into structured analysis.

    Input:  state["jd_text"]
    Output: {"jd_analysis": {role, skills, keywords, tone}}
    """
    llm = get_llm("fast")

    messages = [
        {"role": "system", "content": INTAKE_PROMPT},
        {"role": "user", "content": f"Job description:\n\n{state['jd_text']}"},
    ]

    response = llm.invoke(messages)
    analysis = _parse_json_response(response.content)

    # Sanity check: required keys
    required = {"role", "skills", "keywords", "tone"}
    missing = required - set(analysis.keys())
    if missing:
        raise ValueError(f"Intake LLM response missing keys: {missing}")

    return {"jd_analysis": analysis}

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

    return {"cover_letter_tex": tex}


def _compute_ats_score(tailored_tex: str, keywords: list) -> tuple[float, int, int]:
    """
    Deterministic ATS keyword coverage.
    Case-insensitive substring match: a keyword counts if it appears anywhere
    in the tailored text.
    Returns: (score, matched_count, total_count)
    """
    if not keywords:
        return 1.0, 0, 0

    text_lower = tailored_tex.lower()
    matched = [kw for kw in keywords if kw.lower() in text_lower]
    return len(matched) / len(keywords), len(matched), len(keywords)


def evaluate(state: AppState) -> dict:
    """
    Score the generated outputs on truthfulness, ATS coverage, and tone.
    Truthfulness and tone come from the LLM; ATS is computed deterministically.

    Input:  state["base_resume"], state["tailored_resume_tex"],
            state["cover_letter_tex"], state["jd_analysis"]
    Output: {"eval_report": {...}, "retry_count": incremented}
    """
    llm = get_llm("fast")

    tailored = state.get("tailored_resume_tex") or "(not generated)"
    letter = state.get("cover_letter_tex") or "(not generated)"

    user_content = (
        f"BASE RESUME (ground truth):\n\n{state['base_resume']}\n\n"
        f"---\n\n"
        f"TAILORED RESUME:\n\n{tailored}\n\n"
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

    required = {"passed", "truthfulness_score", "ats_score", "tone_score", "issues"}
    missing = required - set(report.keys())
    if missing:
        raise ValueError(f"Evaluator response missing keys: {missing}")

    # Clamp LLM-provided scores (truthfulness, tone) to [0, 1]
    for key in ("truthfulness_score", "tone_score"):
        report[key] = max(0.0, min(1.0, float(report[key])))

    # Override ATS score with deterministic computation — covers BOTH resume and cover letter
    keywords = state["jd_analysis"].get("keywords", [])
    combined_text = (state.get("tailored_resume_tex") or "") + "\n" + (state.get("cover_letter_tex") or "")
    ats_score, matched, total = _compute_ats_score(combined_text, keywords)
    report["ats_score"] = ats_score

    # Ensure issues is a list
    if not isinstance(report["issues"], list):
        report["issues"] = [str(report["issues"])]

    # Replace the LLM's ATS issue (if any) with our deterministic one
    report["issues"] = [i for i in report["issues"] if "ats" not in i.lower() and "keyword" not in i.lower()]
    if ats_score < 0.6:
            report["issues"].append(
                f"ATS coverage below minimum: {matched}/{total} JD keywords matched ({ats_score:.0%}). Minimum is 60%."
            )

    # Compute `passed` deterministically — ATS threshold is now 0.8
    # Compute `passed` deterministically
    report["passed"] = (
        report["truthfulness_score"] >= 0.8
        and report["ats_score"] >= 0.6
        and report["tone_score"] >= 0.6
    )

    new_retry_count = state.get("retry_count", 0) + 1

    return {
        "eval_report": report,
        "retry_count": new_retry_count,
    }