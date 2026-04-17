from typing import TypedDict, Optional, Literal


class AppState(TypedDict):
    # === Input ===
    user_id: str
    jd_text: str
    request_type: Literal["resume", "cover_letter", "both"]

    # === Loaded from storage ===
    base_resume: str

    # === Intake output ===
    jd_analysis: Optional[dict]

    # === Pre-tailoring ATS check (NEW in Phase 5) ===
    ats_precheck: Optional[dict]  # {baseline_score, matched_keywords, missing_keywords}

    # === Generation outputs ===
    tailored_resume_tex: Optional[str]
    cover_letter_tex: Optional[str]

    # === Evaluator output ===
    eval_report: Optional[dict]
    retry_count: int

    # === Human-in-the-loop ===
    user_decision: Optional[Literal["approve", "revise", "proceed", "augment"]]
    user_feedback: Optional[str]

    # === PDF (deferred — UI compiles on demand) ===
    pdf_bytes: Optional[dict]