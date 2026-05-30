"""
Experience schemas for request/response validation
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date, datetime
from enum import Enum


class EmploymentType(str, Enum):
    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    CONTRACT = "CONTRACT"
    FREELANCE = "FREELANCE"
    INTERNSHIP = "INTERNSHIP"


class ExperienceBase(BaseModel):
    """Base experience schema"""
    title: str = Field(..., min_length=1, max_length=255)
    company: str = Field(..., min_length=1, max_length=255)
    employment_type: EmploymentType = EmploymentType.FULL_TIME
    description: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    sort_order: int = 0


class ExperienceCreate(ExperienceBase):
    """Schema for creating an experience"""
    skill_ids: Optional[List[int]] = []


class ExperienceUpdate(BaseModel):
    """Schema for updating an experience"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    company: Optional[str] = Field(None, min_length=1, max_length=255)
    employment_type: Optional[EmploymentType] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    sort_order: Optional[int] = None
    skill_ids: Optional[List[int]] = None


class ExperienceSkillResponse(BaseModel):
    """Schema for skill nested in an experience response"""
    id: int
    name: str
    icon_url: Optional[str] = None

    class Config:
        from_attributes = True


class ExperienceResponse(ExperienceBase):
    """Schema for experience response"""
    id: int
    created_at: datetime
    updated_at: datetime
    skills: List[ExperienceSkillResponse] = Field(default=[], validation_alias="experience_skills")

    @field_validator("skills", mode="before")
    @classmethod
    def extract_skills(cls, v):
        if not v:
            return []
        result = []
        for item in v:
            if hasattr(item, "skill") and item.skill is not None:
                result.append({
                    "id": item.skill.id,
                    "name": item.skill.name,
                    "icon_url": getattr(item.skill, "icon_url", None),
                })
            elif isinstance(item, dict):
                result.append(item)
            else:
                result.append(item)
        return result

    class Config:
        from_attributes = True
        populate_by_name = True
