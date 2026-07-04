"""
Strength model
"""
from sqlalchemy import Column, BigInteger, String, Integer, DateTime
from datetime import datetime

from app.core.database import Base


class Strength(Base):
    """Strength model"""
    __tablename__ = "strengths"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    description = Column(String(500), nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
