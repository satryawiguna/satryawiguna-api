"""
Education model
"""
from sqlalchemy import Column, BigInteger, String, Integer, DateTime
from datetime import datetime

from app.core.database import Base


class Education(Base):
    """Education model"""
    __tablename__ = "educations"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    degree = Column(String(255), nullable=False)
    institution = Column(String(255), nullable=False)
    start_year = Column(Integer, nullable=False)
    end_year = Column(Integer, nullable=True)
    sort_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
