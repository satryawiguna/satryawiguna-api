"""
Project and ProjectImage models
"""
from sqlalchemy import Column, BigInteger, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Project(Base):
    """Project model"""
    __tablename__ = "projects"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    featured = Column(Boolean, default=False, nullable=False)
    demo_url = Column(String(255), nullable=True)
    repository_url = Column(String(255), nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    project_images = relationship("ProjectImage", back_populates="project", cascade="all, delete-orphan")


class ProjectImage(Base):
    """ProjectImage model (pivot table)"""
    __tablename__ = "project_images"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    project_id = Column(BigInteger, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    image_url = Column(String(500), nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="project_images")
