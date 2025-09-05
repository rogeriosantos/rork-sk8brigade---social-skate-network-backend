from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

try:
    from app.core.database_sync import Base
except ImportError:
    from app.core.database import Base


class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    spot_id = Column(UUID(as_uuid=True), ForeignKey("spots.id"), nullable=False)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    scheduled_date = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer)  # Expected duration in minutes
    max_participants = Column(Integer)
    skill_level = Column(String(20))  # 'Beginner', 'Intermediate', 'Advanced', 'Mixed'
    is_public = Column(Boolean, default=True)
    is_cancelled = Column(Boolean, default=False)
    status = Column(String(20), default="scheduled")  # 'scheduled', 'active', 'completed', 'cancelled'
    tags = Column(JSON)  # Session tags/categories
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", back_populates="sessions_created")
    spot = relationship("Spot", back_populates="sessions")
    participants = relationship("SessionParticipant", back_populates="session", cascade="all, delete-orphan")
    posts = relationship("Post", back_populates="session")


class SessionParticipant(Base):
    __tablename__ = "session_participants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status = Column(String(20), default="joined")  # 'joined', 'maybe', 'declined', 'attended'
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    session = relationship("Session", back_populates="participants")
    user = relationship("User")