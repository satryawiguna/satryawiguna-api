"""
Other schemas (Skill, Media, Setting)
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime


class SkillBase(BaseModel):
    """Base skill schema"""
    name: str = Field(..., min_length=1, max_length=255)
    category_id: Optional[int] = None
    level: Optional[int] = Field(None, ge=0, le=100)
    icon_url: Optional[str] = Field(None, max_length=500)
    sort_order: int = 0


class SkillCreate(SkillBase):
    """Schema for creating a skill"""
    pass


class SkillUpdate(BaseModel):
    """Schema for updating a skill"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    category_id: Optional[int] = None
    level: Optional[int] = Field(None, ge=0, le=100)
    icon_url: Optional[str] = Field(None, max_length=500)
    sort_order: Optional[int] = None


class SkillCategoryResponse(BaseModel):
    """Schema for the category nested within a skill response"""
    id: int
    name: str
    slug: str
    type: str

    class Config:
        from_attributes = True


class SkillResponse(BaseModel):
    """Schema for skill response"""
    id: int
    name: str
    category_id: Optional[int] = None
    level: Optional[int] = None
    icon_url: Optional[str] = None
    sort_order: int = 0
    category: Optional[SkillCategoryResponse] = None

    class Config:
        from_attributes = True


class MediaBase(BaseModel):
    """Base media schema"""
    file_name: str = Field(..., min_length=1, max_length=255)
    file_path: str = Field(..., min_length=1, max_length=500)
    mime_type: Optional[str] = Field(None, max_length=100)
    size: Optional[int] = None



class MediaCreate(MediaBase):
    """Schema for creating a media"""
    pass


class MediaResponse(MediaBase):
    """Schema for media response"""
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class MediaUploadResponse(BaseModel):
    """Schema for media upload response — includes the full public URL"""
    id: str
    file_name: str
    url: str
    mime_type: Optional[str] = None
    size: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SettingBase(BaseModel):
    """Base setting schema"""
    key: str = Field(..., min_length=1, max_length=255)
    value: Optional[str] = None


class SettingCreate(SettingBase):
    """Schema for creating a setting"""
    pass


class SettingUpdate(BaseModel):
    """Schema for updating a setting"""
    value: Optional[str] = None


class SettingResponse(SettingBase):
    """Schema for setting response"""
    id: int
    
    class Config:
        from_attributes = True
