import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, String
from app.database import Base


class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class UUIDMixin:
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
