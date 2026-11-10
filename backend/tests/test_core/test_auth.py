"""Tests for JWT auth core and FastAPI dependency injection."""

import time

import jwt
import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from core.auth import decode_jwt, get_user_from_payload
from core.settings import settings

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_token(overrides: dict | None = None) -> str:
    """Create a valid test JWT signed with the project's secret."""
    payload = {
        "sub": "550e8400-e29b-41b4-941e-001a00000001",
        "email": "test@example.com",
        "exp": int(time.time()) + 300,
        "iat": int(time.time()),
        "app_metadata": {"role": "authenticated"},
    }
    if overrides:
        payload.update(overrides)
    return jwt.encode(payload, settings.supabase_jwt_secret, algorithm="HS256")


# ---------------------------------------------------------------------------
# core.auth tests
# ---------------------------------------------------------------------------


class TestDecodeJwt:
    def test_valid_token(self):
        token = _make_token()
        payload = decode_jwt(token)
        assert payload["sub"] == "550e8400-e29b-41b4-941e-001a00000001"
        assert payload["email"] == "test@example.com"

    def test_strips_bearer_prefix(self):
        token = _make_token()
        payload = decode_jwt(f"Bearer {token}")
        assert payload["sub"] is not None

    def test_expired_token(self):
        payload = _make_token({"exp": int(time.time()) - 10})
        with pytest.raises(jwt.ExpiredSignatureError):
            decode_jwt(payload)

    def test_bad_signature(self):
        token = jwt.encode(
            {"sub": "x", "exp": int(time.time()) + 300, "iat": int(time.time())},
            "wrong-secret",
            algorithm="HS256",
        )
        with pytest.raises(jwt.InvalidSignatureError):
            decode_jwt(token)

    def test_missing_required_claims(self):
        # Missing 'exp'
        token = jwt.encode(
            {"sub": "x", "iat": int(time.time())},
            settings.supabase_jwt_secret,
            algorithm="HS256",
        )
        with pytest.raises((jwt.DecodeError, jwt.exceptions.MissingRequiredClaimError)):
            decode_jwt(token)


class TestGetUserFromPayload:
    def test_default_role(self):
        payload = {"sub": "u1", "email": "a@b.com", "exp": 999, "iat": 1}
        user = get_user_from_payload(payload)
        assert user["id"] == "u1"
        assert user["email"] == "a@b.com"
        assert user["role"] == "authenticated"

    def test_admin_role(self):
        payload = {
            "sub": "admin-1",
            "email": "admin@b.com",
            "app_metadata": {"role": "admin"},
        }
        user = get_user_from_payload(payload)
        assert user["role"] == "admin"

    def test_empty_email(self):
        payload = {"sub": "u2"}
        user = get_user_from_payload(payload)
        assert user["email"] == ""


# ---------------------------------------------------------------------------
# api.deps (FastAPI dependency) tests
# ---------------------------------------------------------------------------


class TestGetCurrentUser:
    @pytest.fixture()
    def client(self) -> TestClient:
        from api.deps import get_current_user

        app = FastAPI()

        @app.get("/me")
        async def me(user=Depends(get_current_user)):  # noqa: B008
            return user

        return TestClient(app)

    def test_no_authorization_header(self, client: TestClient):
        resp = client.get("/me")
        assert resp.status_code == 401
        assert "Not authenticated" in resp.json()["detail"]

    def test_valid_token(self, client: TestClient):
        token = _make_token()
        resp = client.get("/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "550e8400-e29b-41b4-941e-001a00000001"
        assert data["email"] == "test@example.com"

    def test_invalid_token(self, client: TestClient):
        resp = client.get("/me", headers={"Authorization": "Bearer bad.token.here"})
        assert resp.status_code == 401
        assert "Invalid token" in resp.json()["detail"]


class TestRequireAdmin:
    @pytest.fixture()
    def client(self) -> TestClient:
        from api.deps import require_admin

        app = FastAPI()

        @app.get("/admin")
        async def admin_only(user=Depends(require_admin)):  # noqa: B008
            return {"role": user["role"]}

        return TestClient(app)

    def test_authenticated_user_rejected(self, client: TestClient):
        token = _make_token()  # role="authenticated"
        resp = client.get("/admin", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 403
        assert "Admin access required" in resp.json()["detail"]

    def test_admin_user_accepted(self, client: TestClient):
        token = _make_token({"app_metadata": {"role": "admin"}})
        resp = client.get("/admin", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["role"] == "admin"
