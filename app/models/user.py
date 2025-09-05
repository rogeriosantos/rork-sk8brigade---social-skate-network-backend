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
    avatar = Column(String(500))
    bio = Column(Text)
    location = Column(String(255))
    account_type = Column(String(20), nullable=False)  # 'skater' or 'skateshop'
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    followers_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    sessions_created = relationship("Session", back_populates="creator", cascade="all, delete-orphan")
    spots_created = relationship("Spot", back_populates="creator", cascade="all, delete-orphan")
    skater_profile = relationship("SkaterProfile", back_populates="user", uselist=False)
    shop_profile = relationship("ShopProfile", back_populates="user", uselist=False)
    followers = relationship("UserFollow", foreign_keys="UserFollow.following_id", back_populates="following")
    following = relationship("UserFollow", foreign_keys="UserFollow.follower_id", back_populates="follower")


class SkaterProfile(Base):
    __tablename__ = "skater_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    setup = Column(JSON)  # Store skate setup as JSON
    skills = Column(JSON)  # Store skills as JSON array
    preferences = Column(JSON)  # Store preferences as JSON
    joined_shops = Column(JSON)  # Store joined shop IDs as JSON array
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="skater_profile")


class ShopProfile(Base):
    __tablename__ = "shop_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    address = Column(String(500))
    phone = Column(String(20))
    website = Column(String(255))
    brands = Column(JSON)  # Store brands as JSON array
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="shop_profile")


class UserFollow(Base):
    __tablename__ = "user_follows"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    follower_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    following_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    follower = relationship("User", foreign_keys=[follower_id], back_populates="following")
    following = relationship("User", foreign_keys=[following_id], back_populates="followers")