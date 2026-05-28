"""
Skill, Media and Settings models
"""
from sqlalchemy import Column, BigInteger, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Skill(Base):
    """Skill model"""
    __tablename__ = "skills"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    category_id = Column(BigInteger, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    level = Column(Integer, nullable=True)
    icon_url = Column(String(500), nullable=True)
    sort_order = Column(Integer, default=0, nullable=False)
    
    # Relationships
    category = relationship("Category", back_populates="skills")
    project_skills = relationship("ProjectSkill", back_populates="skill", cascade="all, delete-orphan")
    

class Media(Base):
    """Media model"""
    __tablename__ = "media"
    
    id = Column(String(36), primary_key=True, index=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    mime_type = Column(String(100), nullable=True)
    size = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Setting(Base):
    """Setting model"""
    __tablename__ = "settings"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    key = Column(String(255), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=True)
