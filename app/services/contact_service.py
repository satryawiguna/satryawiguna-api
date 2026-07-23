"""
Contact service for handling contact form submissions
"""
import logging

from app.utils.email import send_contact_email
from app.utils.recaptcha import verify_recaptcha_token

logger = logging.getLogger(__name__)


class ContactService:
    """Service for contact form business logic"""

    async def send_contact(
        self,
        identity: str,
        email_address: str,
        transmission: str,
        recaptcha_token: str,
    ) -> dict:
        """
        Send a contact form notification email to the site owner.

        Verifies the reCAPTCHA Enterprise token first; raises
        ``BusinessLogicError`` if the token is invalid or the risk
        score is below the configured threshold.

        Args:
            identity: The sender's name.
            email_address: The sender's email address.
            transmission: The message content.
            recaptcha_token: reCAPTCHA Enterprise token from the frontend.

        Returns:
            A dict with submission details and delivery status.
        """
        # Verify reCAPTCHA before processing the submission
        await verify_recaptcha_token(recaptcha_token)

        email_sent = await send_contact_email(identity, email_address, transmission)

        if not email_sent:
            logger.warning(
                f"Contact email failed to send — name={identity}, email={email_address}"
            )

        return {
            "identity": identity,
            "email_address": email_address,
            "email_sent": email_sent,
        }
