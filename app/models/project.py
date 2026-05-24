"""
Project, ProjectImage, ProjectSkill, ProjectCategory models
"""
import uuid
from sqlalchemy import Column, BigInteger, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Project(Base):
    """Project model"""
    __tablename__ = "projects"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    sub_title = Column(String(255), nullable=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    demo_url = Column(String(255), nullable=True)
    repository_url = Column(String(255), nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    project_images = relationship("ProjectImage", back_populates="project", cascade="all, delete-orphan")
    project_skills = relationship("ProjectSkill", back_populates="project", cascade="all, delete-orphan")
    project_categories = relationship("ProjectCategory", back_populates="project", cascade="all, delete-orphan")


class ProjectImage(Base):
    """ProjectImage model"""
    __tablename__ = "project_images"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    project_id = Column(BigInteger, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    image_url = Column(String(500), nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="project_images")


class ProjectSkill(Base):
    """ProjectSkill pivot model"""
    __tablename__ = "project_skills"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(BigInteger, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(BigInteger, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="project_skills")
    skill = relationship("Skill", back_populates="project_skills")


class ProjectCategory(Base):
    """ProjectCategory pivot model"""
    __tablename__ = "project_categories"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(BigInteger, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(BigInteger, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="project_categories")
    category = relationship("Category", back_populates="project_categories")
