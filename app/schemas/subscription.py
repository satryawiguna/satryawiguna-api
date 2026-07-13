"""
Subscription schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class SubscribeRequest(BaseModel):
    """Schema for subscribing an email"""
    email: EmailStr


class UnsubscribeRequest(BaseModel):
    """Schema for unsubscribing an email"""
    email: EmailStr


class SubscriptionResponse(BaseModel):
    """Schema for subscription response"""
    id: int
    email: str
    verified_at: Optional[datetime] = None
    subscribed_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True
