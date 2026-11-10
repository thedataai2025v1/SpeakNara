"""Test Supabase client creation (mocked)."""

from unittest.mock import MagicMock, patch

import pytest


def test_get_supabase_creates_client():
    """get_supabase delegates to create_client with settings values."""
    mock_client = MagicMock()

    with (
        patch(
            "backend.core.supabase.create_client", return_value=mock_client
        ) as mock_create,
        patch("backend.core.supabase.settings") as mock_settings,
    ):
        mock_settings.supabase_url = "https://test.supabase.co"
        mock_settings.supabase_service_key = "test-key"

        # Force reset
        import backend.core.supabase as sb_module
        from backend.core.supabase import get_supabase

        sb_module._client = None

        client = get_supabase()

        mock_create.assert_called_once_with(
            "https://test.supabase.co",
            "test-key",
        )
        assert client is mock_client


def test_get_supabase_is_singleton():
    """get_supabase returns the same client on subsequent calls."""
    mock_client = MagicMock()

    with (
        patch("backend.core.supabase.create_client", return_value=mock_client),
        patch("backend.core.supabase.settings"),
    ):
        import backend.core.supabase as sb_module

        sb_module._client = None

        client1 = sb_module.get_supabase()
        client2 = sb_module.get_supabase()

        assert client1 is client2


def test_get_supabase_raises_without_url():
    """get_supabase raises if SUPABASE_URL is empty."""
    with (
        patch("backend.core.supabase.settings") as mock_settings,
        patch(
            "backend.core.supabase.create_client", side_effect=ValueError("invalid url")
        ),
    ):
        mock_settings.supabase_url = ""
        mock_settings.supabase_service_key = "key"

        import backend.core.supabase as sb_module

        sb_module._client = None

        with pytest.raises(ValueError):
            sb_module.get_supabase()
