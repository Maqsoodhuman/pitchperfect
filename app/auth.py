"""
Supabase auth helpers for Pitch Perfect.

Wraps signup, signin, and signout with clean return types the
Streamlit UI can check without touching the raw Supabase client.
"""

import os
from typing import Optional, NamedTuple
from supabase import create_client, Client


_client: Optional[Client] = None


class AuthResult(NamedTuple):
    """Structured result from an auth operation."""
    success: bool
    user_id: Optional[str]
    access_token: Optional[str]
    error: Optional[str]


def _get_client() -> Client:
    """
    Lazy-init the Supabase client using the PUBLISHABLE (anon) key.
    Auth operations should NOT use the service key — they run on
    behalf of end users.
    """
    global _client
    if _client is None:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_ANON_KEY")
        if not url or not key:
            raise RuntimeError(
                "SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment."
            )
        _client = create_client(url, key)
    return _client


def sign_up(email: str, password: str) -> AuthResult:
    """
    Create a new user account.
    Returns AuthResult with user_id + access_token on success.
    Email confirmation is disabled in dev, so the new user is
    immediately usable.
    """
    try:
        sb = _get_client()
        response = sb.auth.sign_up(
            {"email": email, "password": password}
        )
        if response.user is None:
            return AuthResult(False, None, None, "Signup failed: no user returned")

        # After signup with confirmation disabled, the session is active
        session = response.session
        access_token = session.access_token if session else None

        return AuthResult(
            success=True,
            user_id=response.user.id,
            access_token=access_token,
            error=None,
        )
    except Exception as e:
        return AuthResult(False, None, None, _friendly_error(str(e)))


def sign_in(email: str, password: str) -> AuthResult:
    """
    Log in an existing user with email + password.
    Returns AuthResult with user_id + access_token on success.
    """
    try:
        sb = _get_client()
        response = sb.auth.sign_in_with_password(
            {"email": email, "password": password}
        )
        if response.user is None or response.session is None:
            return AuthResult(False, None, None, "Login failed: invalid credentials")

        return AuthResult(
            success=True,
            user_id=response.user.id,
            access_token=response.session.access_token,
            error=None,
        )
    except Exception as e:
        return AuthResult(False, None, None, _friendly_error(str(e)))


def sign_out() -> None:
    """
    Log out the current session. Safe to call even if already signed out.
    """
    try:
        sb = _get_client()
        sb.auth.sign_out()
    except Exception:
        pass  # best-effort logout


def _friendly_error(raw: str) -> str:
    """
    Map raw Supabase/Postgrest errors to human-friendly messages.
    Unknown errors fall through as-is.
    """
    raw_lower = raw.lower()
    if "invalid login credentials" in raw_lower:
        return "Incorrect email or password."
    if "user already registered" in raw_lower:
        return "An account with this email already exists. Try logging in instead."
    if "password" in raw_lower and ("short" in raw_lower or "weak" in raw_lower):
        return "Password must be at least 6 characters."
    if "email" in raw_lower and "invalid" in raw_lower:
        return "Please enter a valid email address."
    return raw