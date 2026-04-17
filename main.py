from dotenv import load_dotenv
load_dotenv()

from app.graph import graph
from app.storage import save_resume
from test_fixtures import SAMPLE_RESUME_TEX, SAMPLE_JD


TEST_USER_ID = "11111111-1111-1111-1111-111111111111"


def run():
    print("Saving test resume to Supabase...")
    save_resume(TEST_USER_ID, SAMPLE_RESUME_TEX)
    print(f"saved for user {TEST_USER_ID}\n")

    initial_state = {
        "user_id": TEST_USER_ID,
        "jd_text": SAMPLE_JD,
        "request_type": "both",
        "retry_count": 0,
        # NOTE: no base_resume here — intake loads it from the DB
    }

    print("=" * 60)
    print("  PitchPerfect Phase to End-to-End Run")
    print("=" * 60)
    print(f"User ID:      {TEST_USER_ID}")
    print(f"Request type: {initial_state['request_type']}")
    print(f"JD:           {len(SAMPLE_JD)} chars")
    print()

    final_state = graph.invoke(initial_state)

    print("\n" + "=" * 60)
    print("  JD Analysis")
    print("=" * 60)
    analysis = final_state.get("jd_analysis", {})
    print(f"Role:     {analysis.get('role')}")
    print(f"Tone:     {analysis.get('tone')}")
    print(f"Skills:   {analysis.get('skills')}")
    print(f"Keywords: {analysis.get('keywords')}")

    print("\n" + "=" * 60)
    print("  Base Resume (loaded from DB)")
    print("=" * 60)
    loaded = final_state.get("base_resume", "")
    print(f"Length: {len(loaded)} chars")
    print(f"Match:  {'matches fixture' if loaded == SAMPLE_RESUME_TEX else 'mismatch'}")

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
    print(f"Divergence score:   {report.get('divergence_score', 0):.2f}  (1.0 = no changes, 0.0 = heavy rewriting)")
    print(f"ATS score:          {report.get('ats_score', 0):.2f}")
    print(f"Tone score:         {report.get('tone_score', 0):.2f}")
    print(f"Retry count:        {final_state.get('retry_count')}")
    print(f"Matched keywords:   {report.get('matched_keywords', [])}")
    print(f"Missing keywords:   {report.get('missing_keywords', [])}")
    print(f"Issues ({len(report.get('issues', []))}):")
    for i, issue in enumerate(report.get("issues", []), 1):
        print(f"  {i}. {issue}")

    added = report.get("added_items", [])
    print(f"\nAdded items ({len(added)}) content in tailored output NOT in base resume:")
    if added:
        for item in added:
            print(f"  + {item}")
        print("  (Surfaced for transparency. In Phase 5 you'll confirm or reject each one.)")
    else:
        print("  (none)")

    if tailored:
        with open("output_resume.tex", "w") as f:
            f.write(tailored)
        print("\nTailored resume saved to output_resume.tex")

    if letter:
        with open("output_cover_letter.tex", "w") as f:
            f.write(letter)
        print("Cover letter saved to output_cover_letter.tex")

    print("\n" + "=" * 60)
    print("  Phase 2 end-to-end run complete")
    print("=" * 60)


if __name__ == "__main__":
    run()