"""
Project schemas for request/response validation
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from datetime import datetime


class ProjectBase(BaseModel):
    """Base project schema"""
    title: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    content: Optional[str] = None
    featured: bool = False
    demo_url: Optional[str] = None
    repository_url: Optional[str] = None
    thumbnail_url: Optional[str] = None


class ProjectCreate(ProjectBase):
    """Schema for creating a project"""
    pass


class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    slug: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    content: Optional[str] = None
    featured: Optional[bool] = None
    demo_url: Optional[str] = None
    repository_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    published_at: Optional[datetime] = None


class ProjectResponse(ProjectBase):
    """Schema for project response"""
    id: int
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
