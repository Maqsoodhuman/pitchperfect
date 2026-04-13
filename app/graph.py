"""
LangGraph StateGraph wiring for the PitchPerfect agent pipeline.

Phase 1: intake → (tailor / cover_letter / both) → evaluate → END (with retry loop)

Later phases will add:
- compile_pdf node (Phase 4)
- human_approval interrupt (Phase 5)
"""

from langgraph.graph import StateGraph, END

from app.state import AppState
from app.nodes import intake, tailor_resume, cover_letter, evaluate


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
        return "tailor_resume"  # tailor first, then cover_letter

    raise ValueError(f"Unknown request_type: {request_type}")


def route_after_tailor(state: AppState) -> str:
    """
    After tailor_resume, either go to cover_letter (if request is "both")
    or straight to evaluate (if request is "resume" only).
    """
    if state["request_type"] == "both":
        return "cover_letter"
    return "evaluate"


def route_after_evaluate(state: AppState) -> str:
    """
    After evaluate, decide to end, retry, or give up.

    - passed → END
    - not passed AND retry_count < 2 → retry from the appropriate generation node
    - not passed AND retry_count >= 2 → END (give up, downstream human review)
    """
    report = state.get("eval_report") or {}
    passed = report.get("passed", False)
    retry_count = state.get("retry_count", 0)

    if passed:
        return END

    if retry_count >= 2:
        # Give up retrying; in Phase 5 the human approval step will take over
        return END

    # Retry: route back to the first generation node for this request_type
    request_type = state["request_type"]
    if request_type == "resume":
        return "tailor_resume"
    if request_type == "cover_letter":
        return "cover_letter"
    if request_type == "both":
        return "tailor_resume"

    return END


# ============================================================
# Build the graph
# ============================================================

def build_graph():
    """
    Construct and compile the StateGraph.
    Returns a compiled graph ready for .invoke().
    """
    builder = StateGraph(AppState)

    # Register nodes
    builder.add_node("intake", intake)
    builder.add_node("tailor_resume", tailor_resume)
    builder.add_node("cover_letter", cover_letter)
    builder.add_node("evaluate", evaluate)

    # Entry point
    builder.set_entry_point("intake")

    # After intake, route to the right generation node
    builder.add_conditional_edges(
        "intake",
        route_after_intake,
        {
            "tailor_resume": "tailor_resume",
            "cover_letter": "cover_letter",
        },
    )

    # After tailor_resume, either go to cover_letter or evaluate
    builder.add_conditional_edges(
        "tailor_resume",
        route_after_tailor,
        {
            "cover_letter": "cover_letter",
            "evaluate": "evaluate",
        },
    )

    # cover_letter always goes to evaluate
    builder.add_edge("cover_letter", "evaluate")

    # After evaluate, route to retry or END
    builder.add_conditional_edges(
        "evaluate",
        route_after_evaluate,
        {
            "tailor_resume": "tailor_resume",
            "cover_letter": "cover_letter",
            END: END,
        },
    )

    return builder.compile()


# Compiled graph instance — import this from main.py
graph = build_graph()