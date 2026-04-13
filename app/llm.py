from typing import Literal
from langchain_openai import ChatOpenAI


LLMRole = Literal["fast", "writer"]


def get_llm(role: LLMRole) -> ChatOpenAI:
    """
    Returns a configured LLM client for the given role.

    - "fast":   used by Intake and Evaluator. Deterministic, cheap, JSON-reliable.
    - "writer": used by Tailor and Cover Letter. Slight temperature for natural prose.
    """
    if role == "fast":
        return ChatOpenAI(model="gpt-4o-mini", temperature=0)

    if role == "writer":
        return ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

    raise ValueError(f"Unknown LLM role: {role}")