from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

try:
    from app.core.database_sync import Base
except ImportError:
    from app.core.database import Base


class Spot(Base):
    __tablename__ = "spots"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String(500))
    spot_type = Column(String(50), nullable=False)  # 'street', 'park', 'bowl', 'vert', etc.
    difficulty = Column(String(20))  # 'Beginner', 'Intermediate', 'Advanced', 'Expert'
    features = Column(JSON)  # Store features as JSON array (rails, stairs, ledges, etc.)
    is_public = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", back_populates="spots_created")
    sessions = relationship("Session", back_populates="spot")
    ratings = relationship("SpotRating", back_populates="spot", cascade="all, delete-orphan")
    images = relationship("SpotImage", back_populates="spot", cascade="all, delete-orphan")


class SpotImage(Base):
    __tablename__ = "spot_images"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    spot_id = Column(UUID(as_uuid=True), ForeignKey("spots.id"), nullable=False)
    image_url = Column(String(500), nullable=False)
    caption = Column(String(255))
    is_primary = Column(Boolean, default=False)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    spot = relationship("Spot", back_populates="images")


class SpotRating(Base):
    __tablename__ = "spot_ratings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    spot_id = Column(UUID(as_uuid=True), ForeignKey("spots.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    review = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    spot = relationship("Spot", back_populates="ratings")
    user = relationship("User")