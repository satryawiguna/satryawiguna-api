"""
Career Impact schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CareerImpactBase(BaseModel):
    """Base career impact schema"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    quote: Optional[str] = Field(None, max_length=500)
    icon_url: Optional[str] = Field(None, max_length=500)
    sort_order: int = 0


class CareerImpactCreate(CareerImpactBase):
    """Schema for creating a career impact"""
    pass


class CareerImpactUpdate(BaseModel):
    """Schema for updating a career impact"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    quote: Optional[str] = Field(None, max_length=500)
    icon_url: Optional[str] = Field(None, max_length=500)
    sort_order: Optional[int] = None


class CareerImpactResponse(CareerImpactBase):
    """Schema for career impact response"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True
