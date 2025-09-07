from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class SkateSetupBase(BaseModel):
    board: Dict[str, str]
    trucks: Dict[str, str]
    wheels: Dict[str, str]
    bearings: Dict[str, str]


class SkateSkill(BaseModel):
    name: str
    level: str  # 'Beginner', 'Intermediate', 'Advanced', 'Pro'


class SkatePreferences(BaseModel):
    style: List[str]
    favorite_spots: List[str]
    session_times: List[str]


class ShopInfo(BaseModel):
    name: str
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    brands: List[str]


class UserBase(BaseModel):
    username: str
    email: EmailStr
    display_name: str
    bio: Optional[str] = None
    location: Optional[str] = None
    account_type: str  # 'skater' or 'skateshop'


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    avatar: Optional[str] = None


class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    avatar: Optional[str] = None


class UserResponse(UserBase):
    id: UUID
    avatar: Optional[str] = None
    followers_count: int
    following_count: int
    is_following: Optional[bool] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class SkaterProfileResponse(BaseModel):
    setup: Optional[SkateSetupBase] = None
    skills: Optional[List[SkateSkill]] = None
    preferences: Optional[SkatePreferences] = None
    joined_shops: Optional[List[str]] = None
    
    class Config:
        from_attributes = True


class ShopProfileResponse(BaseModel):
    name: str
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    brands: List[str]
    
    class Config:
        from_attributes = True


class UserFullResponse(UserResponse):
    skater_profile: Optional[SkaterProfileResponse] = None
    shop_profile: Optional[ShopProfileResponse] = None


class SkaterProfileUpdate(BaseModel):
    setup: Optional[Dict[str, Any]] = None
    skills: Optional[List[str]] = None
    preferences: Optional[Dict[str, Any]] = None


class ShopProfileUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    brands: Optional[List[str]] = None
    id: UUID
    avatar: Optional[str] = None
    followers_count: int
    following_count: int
    is_following: Optional[bool] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class SkaterProfileResponse(BaseModel):
    setup: Optional[SkateSetupBase] = None
    skills: Optional[List[SkateSkill]] = None
    preferences: Optional[SkatePreferences] = None
    joined_shops: Optional[List[str]] = None
    
    class Config:
        from_attributes = True


class ShopProfileResponse(BaseModel):
    name: str
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    brands: List[str]
    
    class Config:
        from_attributes = True


class UserFullResponse(UserResponse):
    skater_profile: Optional[SkaterProfileResponse] = None
    shop_profile: Optional[ShopProfileResponse] = None


class SkaterProfileUpdate(BaseModel):
    setup: Optional[SkateSetupBase] = None
    skills: Optional[List[SkateSkill]] = None
    preferences: Optional[SkatePreferences] = None


class ShopProfileUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    brands: Optional[List[str]] = None