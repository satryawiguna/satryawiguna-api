"""
Education schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class EducationBase(BaseModel):
    """Base education schema"""
    degree: str = Field(..., min_length=1, max_length=255)
    institution: str = Field(..., min_length=1, max_length=255)
    start_year: int
    end_year: Optional[int] = None
    sort_order: int = 0


class EducationCreate(EducationBase):
    """Schema for creating an education"""
    pass


class EducationUpdate(BaseModel):
    """Schema for updating an education"""
    degree: Optional[str] = Field(None, min_length=1, max_length=255)
    institution: Optional[str] = Field(None, min_length=1, max_length=255)
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    sort_order: Optional[int] = None


class EducationResponse(EducationBase):
    """Schema for education response"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True
