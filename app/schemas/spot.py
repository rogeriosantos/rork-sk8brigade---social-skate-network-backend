from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class SpotBase(BaseModel):
    name: str
    description: Optional[str] = None
    latitude: float
    longitude: float
    address: Optional[str] = None
    spot_type: str  # 'street', 'park', 'bowl', 'vert', etc.
    difficulty: Optional[str] = None  # 'Beginner', 'Intermediate', 'Advanced', 'Expert'
    features: Optional[List[str]] = None
    is_public: bool = True


class SpotCreate(SpotBase):
    pass


class SpotUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    spot_type: Optional[str] = None
    difficulty: Optional[str] = None
    features: Optional[List[str]] = None
    is_public: Optional[bool] = None


class SpotResponse(SpotBase):
    id: UUID
    rating: float
    rating_count: int
    creator_id: UUID
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class SpotRatingCreate(BaseModel):
    rating: int  # 1-5 stars
    review: Optional[str] = None


class SpotRatingResponse(BaseModel):
    id: UUID
    spot_id: UUID
    user_id: UUID
    rating: int
    review: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class SpotImageCreate(BaseModel):
    image_url: str
    caption: Optional[str] = None
    is_primary: bool = False


class SpotImageResponse(BaseModel):
    id: UUID
    spot_id: UUID
    image_url: str
    caption: Optional[str]
    is_primary: bool
    uploaded_by: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True