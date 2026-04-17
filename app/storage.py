"""
Supabase storage for user resumes.

One resume per user. Uses the service key (server-side, bypasses RLS).
"""

import os
from typing import Optional

from supabase import create_client, Client


_client: Optional[Client] = None


def _get_client() -> Client:
    """
    Lazy-init the Supabase client. Reads env vars at first call so
    tests can set them after import.
    """
    global _client
    if _client is None:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_KEY")
        if not url or not key:
            raise RuntimeError(
                "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in environment. "
                "Check your .env file and that load_dotenv() runs before calling storage functions."
            )
        _client = create_client(url, key)
    return _client


def get_resume(user_id: str) -> Optional[str]:
    """
    Fetch a user's base resume (LaTeX).
    Returns None if no resume exists for this user.
    """
    sb = _get_client()
    result = (
        sb.table("resumes")
        .select("latex_content")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    if not result.data:
        return None
    return result.data[0]["latex_content"]


def save_resume(user_id: str, latex_content: str) -> None:
    """
    Save or update a user's base resume.
    Uses upsert: creates if missing, updates if exists.
    """
    sb = _get_client()
    sb.table("resumes").upsert(
        {
            "user_id": user_id,
            "latex_content": latex_content,
        }
    ).execute()