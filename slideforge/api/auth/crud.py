"""
CRUD operations for user authentication.
"""
from typing import Optional

from sqlalchemy.orm import Session

from slideforge.core.security import get_password_hash, verify_password
from slideforge.db.models.user import User
from slideforge.schemas.user import UserCreate, UserUpdate


def get_user(db: Session, user_id: int) -> Optional[User]:
    """Get a user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get a user by email."""
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, obj_in: UserCreate) -> User:
    """Create a new user."""
    db_obj = User(
        email=obj_in.email,
        hashed_password=get_password_hash(obj_in.password),
        full_name=obj_in.full_name,
        is_active=obj_in.is_active,
        is_superuser=False,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate a user by email and password."""
    user = get_user_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def update_user(db: Session, user_id: int, obj_in: UserUpdate) -> Optional[User]:
    """Update a user."""
    db_obj = get_user(db, user_id=user_id)
    if not db_obj:
        return None
    
    update_data = obj_in.dict(exclude_unset=True)
    
    # If password is provided, hash it
    if "password" in update_data:
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password
    
    # Update user attributes
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj