"""JWT verification using Supabase JWT secret."""

from __future__ import annotations

from typing import Any

import jwt

from core.settings import settings

ALGORITHM = "HS256"


def decode_jwt(token: str) -> dict[str, Any]:
    """Decode and verify a Supabase JWT.

    Returns the decoded payload dict on success.
    Raises jwt.InvalidSignatureError / jwt.ExpiredSignatureError etc. on failure.
    """
    # Strip "Bearer " prefix if present
    if token.startswith("Bearer "):
        token = token[7:]

    return jwt.decode(
        token,
        settings.supabase_jwt_secret,
        algorithms=[ALGORITHM],
        options={"require": ["exp", "iat", "sub"]},
    )


def get_user_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Extract user info from a decoded JWT payload.

    Returns a dict with id, email, role extracted from Supabase JWT claims.
    """
    user_id = payload.get("sub")
    email = (payload.get("email") or "").strip()

    # Supabase stores custom claims in a "app_metadata" or "user_metadata" key
    app_metadata = payload.get("app_metadata", {})
    _user_metadata = payload.get("user_metadata", {})  # noqa: F841
    role = app_metadata.get("role", "authenticated")

    return {
        "id": user_id,
        "email": email,
        "role": role,
        "raw_payload": payload,
    }


# ---------------------------------------------------------------------------
# Helpers for tests
# ---------------------------------------------------------------------------

_test_secret = "test-secret"  # noqa: S105


def _make_token(payload: dict, secret: str | None = None) -> str:
    """Create a signed JWT for testing.

    Adds standard claims (`exp`, `iat`, `sub`) if not present.
    Uses the configured supabase_jwt_secret so tokens pass decode_jwt.
    """
    import time

    payload = {"iat": time.time(), "exp": time.time() + 3600, **payload}
    if "sub" not in payload:
        payload["sub"] = "550e8400-e29b-41b4-941e-001a00000001"
    secret = secret or settings.supabase_jwt_secret
    return jwt.encode(payload, secret, algorithm=ALGORITHM)
