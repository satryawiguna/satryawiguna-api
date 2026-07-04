"""
Strength schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class StrengthBase(BaseModel):
    """Base strength schema"""
    description: str = Field(..., min_length=1, max_length=500)
    sort_order: int = 0


class StrengthCreate(StrengthBase):
    """Schema for creating a strength"""
    pass


class StrengthUpdate(BaseModel):
    """Schema for updating a strength"""
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    sort_order: Optional[int] = None


class StrengthResponse(StrengthBase):
    """Schema for strength response"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True
