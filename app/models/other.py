"""
Skill, Testimonial, Media and Settings models
"""
from sqlalchemy import Column, BigInteger, String, Text, Integer, Boolean, DateTime
from datetime import datetime

from app.core.database import Base


class Skill(Base):
    """Skill model"""
    __tablename__ = "skills"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    category = Column(String(255), nullable=True)
    level = Column(Integer, nullable=True)
    icon = Column(String(255), nullable=True)
    sort_order = Column(Integer, default=0, nullable=False)


class Testimonial(Base):
    """Testimonial model"""
    __tablename__ = "testimonials"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    position = Column(String(255), nullable=True)
    company = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    avatar_url = Column(String(500), nullable=True)
    featured = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    

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
