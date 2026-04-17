"""
LangGraph StateGraph wiring for the PitchPerfect agent pipeline.

Phase 5: adds SqliteSaver checkpointer and interrupt points for
human-in-the-loop flows (pre-tailoring ATS check + final review).
"""

from pathlib import Path
import sqlite3
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from app.state import AppState
from app.nodes import intake, tailor_resume, cover_letter, evaluate, ats_precheck, human_approval

# ============================================================
# Routing functions
# ============================================================

def route_after_intake(state: AppState) -> str:
    """
    After intake, route to the first generation node based on what
    the user requested.
    """
    request_type = state["request_type"]

    if request_type == "resume":
        return "tailor_resume"
    if request_type == "cover_letter":
        return "cover_letter"
    if request_type == "both":
        return "tailor_resume"

    raise ValueError(f"Unknown request_type: {request_type}")


def route_after_tailor(state: AppState) -> str:
    """
    After tailor_resume, either go to cover_letter (if request is "both")
    or straight to evaluate.
    """
    if state["request_type"] == "both":
        return "cover_letter"
    return "evaluate"


def route_after_evaluate(state: AppState) -> str:
    """
    After evaluate, decide whether to retry (rare) or proceed to the
    human approval interrupt.

    With the auditor-mode evaluator, passing depends only on ATS + tone.
    Failures happen when LaTeX compile errors break things downstream.
    """
    report = state.get("eval_report") or {}
    passed = report.get("passed", False)
    retry_count = state.get("retry_count", 0)

    # Always hand off to human_approval after evaluate, unless we
    # need to retry because something is broken AND we have retries left.
    if not passed and retry_count < 2:
        request_type = state["request_type"]
        if request_type == "resume":
            return "tailor_resume"
        if request_type == "cover_letter":
            return "cover_letter"
        if request_type == "both":
            return "tailor_resume"

    return "human_approval"

def route_after_approval(state: AppState) -> str:
    """
    After the user makes a decision on the human_approval interrupt.

    - "revise" → loop back to the first generation node with feedback
    - anything else (approve, or no decision) → END
    """
    decision = state.get("user_decision")
    if decision == "revise":
        request_type = state["request_type"]
        if request_type == "resume":
            return "tailor_resume"
        if request_type == "cover_letter":
            return "cover_letter"
        if request_type == "both":
            return "tailor_resume"
    return END
# ============================================================
# Build + compile the graph
# ============================================================

_CHECKPOINT_DB_PATH = Path("checkpoints.db")


def build_graph(checkpoint_db: Path | None = None):
    """
    Construct and compile the StateGraph with a SqliteSaver checkpointer.
    Returns a compiled graph ready for .invoke() and .get_state().

    Args:
        checkpoint_db: optional path to the SQLite file. Defaults to
                       ./checkpoints.db in the working directory.
    """
    db_path = checkpoint_db or _CHECKPOINT_DB_PATH

    builder = StateGraph(AppState)

    # Register nodes
    builder.add_node("intake", intake)
    builder.add_node("ats_precheck", ats_precheck)
    builder.add_node("tailor_resume", tailor_resume)
    builder.add_node("cover_letter", cover_letter)
    builder.add_node("evaluate", evaluate)
    builder.add_node("human_approval", human_approval)

    # Entry point
    builder.set_entry_point("intake")

    # intake → ats_precheck
    builder.add_edge("intake", "ats_precheck")

    # ats_precheck → first generation node (same routing as before)
    builder.add_conditional_edges(
        "ats_precheck",
        route_after_intake,
        {
            "tailor_resume": "tailor_resume",
            "cover_letter": "cover_letter",
        },
    )

    # After tailor_resume: cover_letter (if "both") or evaluate
    builder.add_conditional_edges(
        "tailor_resume",
        route_after_tailor,
        {
            "cover_letter": "cover_letter",
            "evaluate": "evaluate",
        },
    )

    # cover_letter → evaluate
    builder.add_edge("cover_letter", "evaluate")

    # After evaluate: retry (if broken) or go to human_approval
    builder.add_conditional_edges(
        "evaluate",
        route_after_evaluate,
        {
            "tailor_resume": "tailor_resume",
            "cover_letter": "cover_letter",
            "human_approval": "human_approval",
        },
    )

    # After human_approval: revise (loop back) or end
    builder.add_conditional_edges(
        "human_approval",
        route_after_approval,
        {
            "tailor_resume": "tailor_resume",
            "cover_letter": "cover_letter",
            END: END,
        },
    )

    # Create the checkpointer and compile with it
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    checkpointer = SqliteSaver(conn)

    return builder.compile(
        checkpointer=checkpointer,
        interrupt_after=["ats_precheck"],
        interrupt_before=["human_approval"],
    )

# Compiled graph instance (module-level singleton)
graph = build_graph()