"""
Contact form API endpoint (public, no auth required)
"""
from fastapi import APIRouter, status

from app.schemas.contact import ContactRequest
from app.services.contact_service import ContactService
from app.utils.response import APIResponse


router = APIRouter()


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Send contact form message",
    description="""Submit a message through the contact form.

    Verifies the request with reCAPTCHA Enterprise before forwarding
    the message. On success, sends a notification email to the site
    owner with the sender's name, email address, and message content.

    This endpoint is public and does **not** require authentication.
    """,
    responses={
        201: {
            "description": "Message sent successfully",
        },
        400: {
            "description": "reCAPTCHA verification failed or bad request",
        },
    },
)
async def send_contact(
    request: ContactRequest,
):
    """
    Submit a contact form message protected by reCAPTCHA Enterprise.
    """
    service = ContactService()
    result = await service.send_contact(
        identity=request.identity,
        email_address=request.email_address,
        transmission=request.transmission,
        recaptcha_token=request.recaptcha_token,
    )
    return APIResponse.success(
        message="Message sent successfully",
        status=status.HTTP_201_CREATED,
        data=result,
    )
