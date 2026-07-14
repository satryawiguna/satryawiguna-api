"""
Subscription model for newsletter email subscriptions
"""
from sqlalchemy import Column, BigInteger, String, DateTime
from datetime import datetime

from app.core.database import Base


class Subscription(Base):
    """Subscription model — stores verified email subscriptions"""
    __tablename__ = "subscriptions"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    verification_token = Column(String(500), unique=True, nullable=True)
    verified_at = Column(DateTime, nullable=True)
    unsubscribed_at = Column(DateTime, nullable=True)
    subscribed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
