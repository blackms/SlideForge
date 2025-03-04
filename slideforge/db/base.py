"""
Base configuration for SQLAlchemy models.
"""
from datetime import datetime
from typing import Any

from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

# Create the SQLAlchemy declarative base
Base = declarative_base()

class TimestampMixin:
    """
    Mixin that adds created_at and updated_at columns to a model.
    """
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)


class BaseModel(Base):
    """
    Abstract base model with common columns and methods.
    """
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    
    def __repr__(self) -> str:
        attrs = []
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            attrs.append(f"{column.name}={value!r}")
        return f"{self.__class__.__name__}({', '.join(attrs)})"
    
    def dict(self) -> dict[str, Any]:
        """
        Convert the model instance to a dictionary.
        """
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
