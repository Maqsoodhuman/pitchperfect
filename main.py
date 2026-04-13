"""
Phase 1 end-to-end entry point.

Runs the full LangGraph pipeline on hardcoded fixtures and prints the result.
No UI, no DB, no PDF generation in Phase 1 — just proof that the agents
work together.

Later phases will replace this with a Streamlit UI (Phase 3) that calls
the same graph with real user inputs.
"""

from dotenv import load_dotenv
load_dotenv()

from app.graph import graph
from test_fixtures import SAMPLE_RESUME_TEX, SAMPLE_JD


def run():
    # Build initial state — the graph expects these fields set upfront.
    # In later phases, `user_id` will drive Supabase lookup for base_resume.
    initial_state = {
        "user_id": "phase1-test-user",
        "jd_text": SAMPLE_JD,
        "request_type": "both",          # "resume" | "cover_letter" | "both"
        "base_resume": SAMPLE_RESUME_TEX,  # hardcoded in Phase 1
        "retry_count": 0,
    }

    print("=" * 60)
    print("  PitchPerfect — Phase 1 End-to-End Run")
    print("=" * 60)
    print(f"Request type: {initial_state['request_type']}")
    print(f"Base resume:  {len(SAMPLE_RESUME_TEX)} chars")
    print(f"JD:           {len(SAMPLE_JD)} chars")
    print()

    # Invoke the compiled graph
    final_state = graph.invoke(initial_state)

    # ===== Pretty-print the result =====

    print("\n" + "=" * 60)
    print("  JD Analysis")
    print("=" * 60)
    analysis = final_state.get("jd_analysis", {})
    print(f"Role:     {analysis.get('role')}")
    print(f"Tone:     {analysis.get('tone')}")
    print(f"Skills:   {analysis.get('skills')}")
    print(f"Keywords: {analysis.get('keywords')}")

    print("\n" + "=" * 60)
    print("  Tailored Resume")
    print("=" * 60)
    tailored = final_state.get("tailored_resume_tex")
    if tailored:
        print(f"Length: {len(tailored)} chars")
        print(f"First 200 chars: {tailored[:200]}")
    else:
        print("(not generated)")

    print("\n" + "=" * 60)
    print("  Cover Letter")
    print("=" * 60)
    letter = final_state.get("cover_letter_tex")
    if letter:
        print(f"Length: {len(letter)} chars")
        print(f"First 200 chars: {letter[:200]}")
    else:
        print("(not generated)")

    print("\n" + "=" * 60)
    print("  Evaluation Report")
    print("=" * 60)
    report = final_state.get("eval_report", {})
    print(f"Passed:             {report.get('passed')}")
    print(f"Truthfulness score: {report.get('truthfulness_score'):.2f}")
    print(f"ATS score:          {report.get('ats_score'):.2f}")
    print(f"Tone score:         {report.get('tone_score'):.2f}")
    print(f"Retry count:        {final_state.get('retry_count')}")
    print(f"Issues ({len(report.get('issues', []))}):")
    for i, issue in enumerate(report.get("issues", []), 1):
        print(f"  {i}. {issue}")

    # Optional: save the tailored outputs to disk so you can compile them manually
    if tailored:
        with open("output_resume.tex", "w") as f:
            f.write(tailored)
        print("\nTailored resume saved to output_resume.tex")

    if letter:
        with open("output_cover_letter.tex", "w") as f:
            f.write(letter)
        print("Cover letter saved to output_cover_letter.tex")

    print("\n" + "=" * 60)
    print("  Phase 1 end-to-end run complete ✅")
    print("=" * 60)


if __name__ == "__main__":
    run()