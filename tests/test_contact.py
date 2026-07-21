"""
Tests for contact form endpoint:
  - Public: POST /api/v1/contact (no auth required)
  - Sends email via SMTP (Brevo) to the site owner
"""
from unittest.mock import patch

import pytest
from httpx import AsyncClient


_CONTACT_PAYLOAD = {
    "identity": "John Doe",
    "email_address": "john@example.com",
    "transmission": "Hello, I would like to discuss a project.",
}


class TestSendContact:
    """Tests for POST /api/v1/contact"""

    @patch("app.utils.email.aiosmtplib.send")
    async def test_send_contact_success(self, mock_send, client: AsyncClient):
        """Successful contact submission returns 201 with email_sent=True."""
        mock_send.return_value = None  # Simulate successful send

        response = await client.post(
            "/api/v1/contact",
            json=_CONTACT_PAYLOAD,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["status"] == 201
        assert data["message"] == "Message sent successfully"
        assert data["data"]["identity"] == "John Doe"
        assert data["data"]["email_address"] == "john@example.com"
        assert data["data"]["email_sent"] is True
        mock_send.assert_called_once()

    @patch("app.utils.email.aiosmtplib.send")
    async def test_send_contact_smtp_failure(self, mock_send, client: AsyncClient):
        """If SMTP fails, the response still returns 201 but email_sent=False."""
        mock_send.side_effect = Exception("SMTP connection refused")

        response = await client.post(
            "/api/v1/contact",
            json=_CONTACT_PAYLOAD,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["email_sent"] is False
        mock_send.assert_called_once()

    async def test_send_contact_missing_identity(self, client: AsyncClient):
        """Missing identity returns 422 validation error."""
        response = await client.post(
            "/api/v1/contact",
            json={
                "email_address": "john@example.com",
                "transmission": "Hello",
            },
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    async def test_send_contact_invalid_email(self, client: AsyncClient):
        """Invalid email returns 422 validation error."""
        response = await client.post(
            "/api/v1/contact",
            json={
                "identity": "John Doe",
                "email_address": "not-an-email",
                "transmission": "Hello",
            },
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    async def test_send_contact_empty_transmission(self, client: AsyncClient):
        """Empty transmission returns 422 validation error."""
        response = await client.post(
            "/api/v1/contact",
            json={
                "identity": "John Doe",
                "email_address": "john@example.com",
                "transmission": "",
            },
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    async def test_send_contact_no_auth_required(self, client: AsyncClient):
        """Contact endpoint returns 201 without any auth headers."""
        response = await client.post(
            "/api/v1/contact",
            json=_CONTACT_PAYLOAD,
        )
        # Should NOT return 401 — public endpoint
        assert response.status_code != 401
