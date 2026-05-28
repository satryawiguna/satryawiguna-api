"""
Project schemas for request/response validation
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime


class ProjectBase(BaseModel):
    """Base project schema"""
    title: str = Field(..., min_length=1, max_length=255)
    sub_title: Optional[str] = Field(None, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    content: Optional[str] = None
    demo_url: Optional[str] = None
    repository_url: Optional[str] = None
    thumbnail_url: Optional[str] = None


class ProjectCreate(ProjectBase):
    """Schema for creating a project"""
    skill_ids: Optional[List[int]] = []
    image_urls: Optional[List[str]] = []
    category_ids: Optional[List[int]] = []


class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    sub_title: Optional[str] = Field(None, max_length=255)
    slug: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    content: Optional[str] = None
    demo_url: Optional[str] = None
    repository_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    published_at: Optional[datetime] = None
    skill_ids: Optional[List[int]] = None
    image_urls: Optional[List[str]] = None
    category_ids: Optional[List[int]] = None


class ProjectImageResponse(BaseModel):
    """Schema for project image response"""
    id: int
    image_url: str

    class Config:
        from_attributes = True


class ProjectSkillResponse(BaseModel):
    """Schema for project skill (nested)"""
    id: int
    name: str
    icon_url: Optional[str] = None

    class Config:
        from_attributes = True


class ProjectCategoryResponse(BaseModel):
    """Schema for project category (nested)"""
    id: int
    name: str
    slug: str

    class Config:
        from_attributes = True


class ProjectResponse(ProjectBase):
    """Schema for project response"""
    id: int
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    images: List[ProjectImageResponse] = Field(default=[], validation_alias="project_images")
    skills: List[ProjectSkillResponse] = Field(default=[], validation_alias="project_skills")
    categories: List[ProjectCategoryResponse] = Field(default=[], validation_alias="project_categories")

    @field_validator('skills', mode='before')
    @classmethod
    def extract_skills(cls, v):
        if not v:
            return []
        result = []
        for item in v:
            if hasattr(item, 'skill') and item.skill is not None:
                result.append({
                    'id': item.skill.id,
                    'name': item.skill.name,
                    'icon_url': getattr(item.skill, 'icon_url', None),
                })
            elif isinstance(item, dict):
                result.append(item)
            else:
                result.append(item)
        return result

    @field_validator('categories', mode='before')
    @classmethod
    def extract_categories(cls, v):
        if not v:
            return []
        result = []
        for item in v:
            if hasattr(item, 'category') and item.category is not None:
                result.append({
                    'id': item.category.id,
                    'name': item.category.name,
                    'slug': item.category.slug,
                })
            elif isinstance(item, dict):
                result.append(item)
            else:
                result.append(item)
        return result
    
    class Config:
        from_attributes = True

