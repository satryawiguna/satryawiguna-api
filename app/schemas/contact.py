"""
Contact form schemas for request validation
"""
from pydantic import BaseModel, EmailStr, Field


class ContactRequest(BaseModel):
    """Schema for contact form submission"""
    identity: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Sender's name",
    )
    email_address: EmailStr = Field(
        ...,
        description="Sender's email address",
    )
    transmission: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Message content",
    )
    recaptcha_token: str = Field(
        ...,
        min_length=1,
        description="reCAPTCHA Enterprise token from the frontend widget",
    )
