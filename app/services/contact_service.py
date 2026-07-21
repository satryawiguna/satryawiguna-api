"""
Contact service for handling contact form submissions
"""
import logging

from app.utils.email import send_contact_email

logger = logging.getLogger(__name__)


class ContactService:
    """Service for contact form business logic"""

    async def send_contact(self, identity: str, email_address: str, transmission: str) -> dict:
        """
        Send a contact form notification email to the site owner.

        Args:
            identity: The sender's name.
            email_address: The sender's email address.
            transmission: The message content.

        Returns:
            A dict with submission details and delivery status.
        """
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
