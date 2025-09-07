from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class SkateSetupResponse(BaseModel):
    id: UUID
    deck_brand: str
    deck_size: str
    trucks: str
    wheels: str
    bearings: str
    grip_tape: str
    photo_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class SkateSetupCreate(BaseModel):
    deck_brand: str
    deck_size: str
    trucks: str
    wheels: str
    bearings: str
    grip_tape: str
    photo_url: Optional[str] = None


class SkateSetupUpdate(BaseModel):
    deck_brand: Optional[str] = None
    deck_size: Optional[str] = None
    trucks: Optional[str] = None
    wheels: Optional[str] = None
    bearings: Optional[str] = None
    grip_tape: Optional[str] = None
    photo_url: Optional[str] = None


class UserBase(BaseModel):
    username: str
    email: EmailStr
    display_name: str
    bio: Optional[str] = None
    is_shop: bool  # Match database schema


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    profile_picture: Optional[str] = None  # Match database schema


class UserResponse(UserBase):
    id: UUID
    profile_picture: Optional[str] = None  # Match database schema
    follower_count: int  # Match database schema
    following_count: int
    is_following: Optional[bool] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserFullResponse(UserResponse):
    skate_setups: Optional[List[SkateSetupResponse]] = None
    # For shops - we could add shop-specific data here if needed