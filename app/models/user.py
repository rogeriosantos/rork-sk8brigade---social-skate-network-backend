from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

try:
    from app.core.database_sync import Base
except ImportError:
    from app.core.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    display_name = Column(String(100), nullable=False)
    bio = Column(Text)
    profile_picture = Column(String(500))  # Match database schema
    is_shop = Column(Boolean, nullable=False)  # Match database schema
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    follower_count = Column(Integer, default=0)  # Match database schema
    following_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships - match actual database tables
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    sessions_created = relationship("Session", back_populates="creator", cascade="all, delete-orphan")  
    spots_created = relationship("Spot", back_populates="creator", cascade="all, delete-orphan")
    skate_setups = relationship("SkateSetup", back_populates="user", cascade="all, delete-orphan")
    follows_as_follower = relationship("Follow", foreign_keys="Follow.follower_id", back_populates="follower")
    follows_as_followed = relationship("Follow", foreign_keys="Follow.followed_id", back_populates="followed")


class SkateSetup(Base):
    __tablename__ = "skate_setups"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deck_brand = Column(String(100), nullable=False)
    deck_size = Column(String(20), nullable=False)  
    trucks = Column(String(100), nullable=False)
    wheels = Column(String(100), nullable=False)
    bearings = Column(String(100), nullable=False)
    grip_tape = Column(String(100), nullable=False)
    photo_url = Column(String(500))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="skate_setups")


class Follow(Base):
    __tablename__ = "follows"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    follower_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    followed_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    follower = relationship("User", foreign_keys=[follower_id], back_populates="follows_as_follower")
    followed = relationship("User", foreign_keys=[followed_id], back_populates="follows_as_followed")