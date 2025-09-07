from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

try:
    from app.core.database_sync import Base
except ImportError:
    from app.core.database import Base


class User(Base):
    __tablename__ = "users"
    
    # Database fields - EXACT match to DDL
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    display_name = Column(String(100), nullable=False)
    bio = Column(Text, nullable=True)
    profile_picture = Column(String(500), nullable=True)
    is_shop = Column(Boolean, nullable=False)
    is_active = Column(Boolean, nullable=False)
    is_verified = Column(Boolean, nullable=False)
    follower_count = Column(Integer, nullable=False)
    following_count = Column(Integer, nullable=False)
    
    # Relationships - match actual database tables ONLY
    skate_setups = relationship("SkateSetup", back_populates="user", cascade="all, delete-orphan")


class SkateSetup(Base):
    __tablename__ = "skate_setups"
    
    # Database fields - EXACT match to DDL
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deck_brand = Column(String(100), nullable=False)
    deck_size = Column(String(20), nullable=False)
    trucks = Column(String(100), nullable=False)
    wheels = Column(String(100), nullable=False)
    bearings = Column(String(100), nullable=False)
    grip_tape = Column(String(100), nullable=False)
    photo_url = Column(String(500), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="skate_setups")