"""
User model for authentication and user management.
"""
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

from slideforge.db.base import BaseModel, TimestampMixin


class User(BaseModel, TimestampMixin):
    """
    User model for authentication and user management.
    """
    __tablename__ = "users"
    
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Relationships
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="user", cascade="all, delete-orphan")