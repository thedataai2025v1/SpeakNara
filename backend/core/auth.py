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
