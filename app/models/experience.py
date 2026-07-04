"""
Experience and ExperienceSkill models
"""
import uuid
from sqlalchemy import Column, BigInteger, String, Text, Integer, Date, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Experience(Base):
    """Experience model"""
    __tablename__ = "experiences"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    employment_type = Column(
        Enum("FULL_TIME", "PART_TIME", "CONTRACT", "FREELANCE", "INTERNSHIP", name="employment_type"),
        nullable=False,
        default="FULL_TIME",
    )
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)  # NULL means "PRESENT"
    sort_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    experience_skills = relationship("ExperienceSkill", back_populates="experience", cascade="all, delete-orphan")


class ExperienceSkill(Base):
    """ExperienceSkill pivot model"""
    __tablename__ = "experience_skills"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    experience_id = Column(BigInteger, ForeignKey("experiences.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(BigInteger, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    experience = relationship("Experience", back_populates="experience_skills")
    skill = relationship("Skill", back_populates="experience_skills")
