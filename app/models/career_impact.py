"""
Career Impact model
"""
from sqlalchemy import Column, BigInteger, String, Text, Integer, DateTime
from datetime import datetime

from app.core.database import Base


class CareerImpact(Base):
    """Career Impact model"""
    __tablename__ = "career_impacts"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    quote = Column(String(500), nullable=True)
    icon_url = Column(String(500), nullable=True)
    sort_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
