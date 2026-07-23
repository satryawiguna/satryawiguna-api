"""
Tests for contact form endpoint:
  - Public: POST /api/v1/contact (no auth required)
  - Verifies reCAPTCHA Enterprise token before sending email
  - Sends email via SMTP (Brevo) to the site owner
"""
from unittest.mock import patch

import pytest
from httpx import AsyncClient

from app.core.exceptions import BusinessLogicError


_CONTACT_PAYLOAD = {
    "identity": "John Doe",
    "email_address": "john@example.com",
    "transmission": "Hello, I would like to discuss a project.",
    "recaptcha_token": "test-recaptcha-token",
}


class TestSendContact:
    """Tests for POST /api/v1/contact"""

    @patch("app.services.contact_service.verify_recaptcha_token")
    @patch("app.utils.email.aiosmtplib.send")
    async def test_send_contact_success(
        self, mock_send, mock_recaptcha, client: AsyncClient
    ):
        """Successful contact submission returns 201 with email_sent=True."""
        mock_recaptcha.return_value = True
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
        mock_recaptcha.assert_called_once_with("test-recaptcha-token")
        mock_send.assert_called_once()

    @patch("app.services.contact_service.verify_recaptcha_token")
    @patch("app.utils.email.aiosmtplib.send")
    async def test_send_contact_smtp_failure(
        self, mock_send, mock_recaptcha, client: AsyncClient
    ):
        """If SMTP fails, the response still returns 201 but email_sent=False."""
        mock_recaptcha.return_value = True
        mock_send.side_effect = Exception("SMTP connection refused")

        response = await client.post(
            "/api/v1/contact",
            json=_CONTACT_PAYLOAD,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["email_sent"] is False
        mock_recaptcha.assert_called_once_with("test-recaptcha-token")
        mock_send.assert_called_once()

    @patch("app.services.contact_service.verify_recaptcha_token")
    async def test_send_contact_invalid_recaptcha(
        self, mock_recaptcha, client: AsyncClient
    ):
        """Invalid reCAPTCHA token returns 400."""
        mock_recaptcha.side_effect = BusinessLogicError(
            "reCAPTCHA verification failed"
        )

        response = await client.post(
            "/api/v1/contact",
            json=_CONTACT_PAYLOAD,
        )

        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert data["status"] == 400
        assert "reCAPTCHA" in data["message"]
        mock_recaptcha.assert_called_once_with("test-recaptcha-token")

    async def test_send_contact_missing_recaptcha(self, client: AsyncClient):
        """Missing recaptcha_token returns 422 validation error."""
        response = await client.post(
            "/api/v1/contact",
            json={
                "identity": "John Doe",
                "email_address": "john@example.com",
                "transmission": "Hello",
            },
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

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
