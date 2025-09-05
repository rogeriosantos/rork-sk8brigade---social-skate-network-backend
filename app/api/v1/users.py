from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User, SkaterProfile, ShopProfile, UserFollow
from app.schemas.user import (
    UserResponse, UserFullResponse, UserUpdate, 
    SkaterProfileUpdate, ShopProfileUpdate
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = None,
    account_type: Optional[str] = Query(None, regex="^(skater|skateshop)$"),
    db: AsyncSession = Depends(get_db)
):
    """Get users with optional filtering and pagination"""
    query = select(User).where(User.is_active == True)
    
    if search:
        search_filter = or_(
            User.username.ilike(f"%{search}%"),
            User.display_name.ilike(f"%{search}%")
        )
        query = query.where(search_filter)
    
    if account_type:
        query = query.where(User.account_type == account_type)
    
    query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    return users


@router.get("/{user_id}", response_model=UserFullResponse)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Get user by ID with full profile information"""
    query = select(User).options(
        selectinload(User.skater_profile),
        selectinload(User.shop_profile)
    ).where(User.id == user_id, User.is_active == True)
    
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if current user follows this user
    if current_user:
        follow_result = await db.execute(
            select(UserFollow).where(
                and_(
                    UserFollow.follower_id == current_user.id,
                    UserFollow.following_id == user_id
                )
            )
        )
        user.is_following = follow_result.scalar_one_or_none() is not None
    
    return user


@router.put("/profile", response_model=UserFullResponse)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user's basic profile"""
    update_data = user_update.model_dump(exclude_unset=True)
    
    if update_data:
        await db.execute(
            update(User)
            .where(User.id == current_user.id)
            .values(**update_data)
        )
        await db.commit()
        await db.refresh(current_user)
    
    return current_user


@router.put("/skater-profile", response_model=UserFullResponse)
async def update_skater_profile(
    profile_update: SkaterProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user's skater profile"""
    if current_user.account_type != "skater":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only skater accounts can update skater profile"
        )
    
    update_data = profile_update.model_dump(exclude_unset=True)
    
    if update_data:
        await db.execute(
            update(SkaterProfile)
            .where(SkaterProfile.user_id == current_user.id)
            .values(**update_data)
        )
        await db.commit()
        await db.refresh(current_user)
    
    return current_user


@router.put("/shop-profile", response_model=UserFullResponse)
async def update_shop_profile(
    profile_update: ShopProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user's shop profile"""
    if current_user.account_type != "skateshop":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only skateshop accounts can update shop profile"
        )
    
    update_data = profile_update.model_dump(exclude_unset=True)
    
    if update_data:
        await db.execute(
            update(ShopProfile)
            .where(ShopProfile.user_id == current_user.id)
            .values(**update_data)
        )
        await db.commit()
        await db.refresh(current_user)
    
    return current_user


@router.post("/{user_id}/follow")
async def follow_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Follow a user"""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot follow yourself"
        )
    
    # Check if user exists
    target_user = await db.execute(select(User).where(User.id == user_id))
    if not target_user.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already following
    existing_follow = await db.execute(
        select(UserFollow).where(
            and_(
                UserFollow.follower_id == current_user.id,
                UserFollow.following_id == user_id
            )
        )
    )
    
    if existing_follow.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already following this user"
        )
    
    # Create follow relationship
    follow = UserFollow(follower_id=current_user.id, following_id=user_id)
    db.add(follow)
    
    # Update follow counts
    await db.execute(
        update(User)
        .where(User.id == current_user.id)
        .values(following_count=User.following_count + 1)
    )
    
    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(followers_count=User.followers_count + 1)
    )
    
    await db.commit()
    
    return {"message": "User followed successfully"}


@router.delete("/{user_id}/follow")
async def unfollow_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Unfollow a user"""
    # Find and delete follow relationship
    result = await db.execute(
        select(UserFollow).where(
            and_(
                UserFollow.follower_id == current_user.id,
                UserFollow.following_id == user_id
            )
        )
    )
    
    follow = result.scalar_one_or_none()
    if not follow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not following this user"
        )
    
    await db.delete(follow)
    
    # Update follow counts
    await db.execute(
        update(User)
        .where(User.id == current_user.id)
        .values(following_count=User.following_count - 1)
    )
    
    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(followers_count=User.followers_count - 1)
    )
    
    await db.commit()
    
    return {"message": "User unfollowed successfully"}


@router.get("/{user_id}/followers", response_model=List[UserResponse])
async def get_user_followers(
    user_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get user's followers"""
    query = (
        select(User)
        .join(UserFollow, User.id == UserFollow.follower_id)
        .where(UserFollow.following_id == user_id)
        .offset(skip)
        .limit(limit)
    )
    
    result = await db.execute(query)
    followers = result.scalars().all()
    
    return followers


@router.get("/{user_id}/following", response_model=List[UserResponse])
async def get_user_following(
    user_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get users that this user is following"""
    query = (
        select(User)
        .join(UserFollow, User.id == UserFollow.following_id)
        .where(UserFollow.follower_id == user_id)
        .offset(skip)
        .limit(limit)
    )
    
    result = await db.execute(query)
    following = result.scalars().all()
    
    return following