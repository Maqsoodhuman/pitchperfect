from typing import TypedDict, Optional, Literal


class AppState(TypedDict):
    # === Input (set at graph invocation) ===
    user_id: str
    jd_text: str
    request_type: Literal["resume", "cover_letter", "both"]

    # === Loaded from storage (Phase 2) — hardcoded for Phase 1 ===
    base_resume: str

    # === Intake agent output ===
    jd_analysis: Optional[dict]  # {role, skills, keywords, tone}

    # === Generation outputs ===
    tailored_resume_tex: Optional[str]
    cover_letter_tex: Optional[str]

    # === Evaluator output ===
    eval_report: Optional[dict]  # {passed, truthfulness_score, ats_score, tone_score, issues}
    retry_count: int

    # === PDF outputs (Phase 4) ===
    pdf_bytes: Optional[dict]

    # === Human-in-the-loop (Phase 5) ===
    user_decision: Optional[Literal["approve", "revise"]]
    user_feedback: Optional[str]