from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.cloudinary import upload_image, delete_image
from app.models.user import User
from app.schemas.user import UserResponse, UserFullResponse, UserUpdate

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
    query = select(User).where(User.id == user_id, User.is_active == True)
    
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if current user follows this user
    if current_user:
        from app.models.user import Follow
        follow_result = await db.execute(
            select(Follow).where(
                and_(
                    Follow.follower_id == current_user.id,
                    Follow.followed_id == user_id
                )
            )
        )
        user.is_following = follow_result.scalar_one_or_none() is not None
    
    # Build response with skate setups if not a shop
    response_data = user.__dict__.copy()
    response_data["id"] = str(user.id)
    
    if not user.is_shop:
        from app.models.user import SkateSetup
        setups_result = await db.execute(
            select(SkateSetup).where(SkateSetup.user_id == user.id)
        )
        setups = setups_result.scalars().all()
        response_data["skate_setups"] = [
            {
                "id": str(setup.id),
                "deck_brand": setup.deck_brand,
                "deck_size": setup.deck_size,
                "trucks": setup.trucks,
                "wheels": setup.wheels,
                "bearings": setup.bearings,
                "grip_tape": setup.grip_tape,
                "photo_url": setup.photo_url,
            }
            for setup in setups
        ]
    
    return response_data


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


@router.post("/skate-setup", response_model=dict)
async def create_skate_setup(
    setup_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new skate setup for the current user"""
    if current_user.is_shop:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Shop accounts cannot create skate setups"
        )
    
    from app.models.user import SkateSetup
    
    # Create new skate setup
    setup = SkateSetup(
        user_id=current_user.id,
        deck_brand=setup_data.get("deck_brand", ""),
        deck_size=setup_data.get("deck_size", ""),
        trucks=setup_data.get("trucks", ""),
        wheels=setup_data.get("wheels", ""),
        bearings=setup_data.get("bearings", ""),
        grip_tape=setup_data.get("grip_tape", ""),
        photo_url=setup_data.get("photo_url")
    )
    
    db.add(setup)
    await db.commit()
    await db.refresh(setup)
    
    return {
        "id": str(setup.id),
        "deck_brand": setup.deck_brand,
        "deck_size": setup.deck_size,
        "trucks": setup.trucks,
        "wheels": setup.wheels,
        "bearings": setup.bearings,
        "grip_tape": setup.grip_tape,
        "photo_url": setup.photo_url,
    }


@router.post("/upload-avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload user avatar image"""
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # Check file size (5MB limit)
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must be less than 5MB"
        )
    
    # Delete old avatar if exists
    if current_user.avatar:
        try:
            # Extract public_id from URL
            old_public_id = current_user.avatar.split('/')[-1].split('.')[0]
            if old_public_id:
                await delete_image(f"sk8brigade/avatars/{old_public_id}")
        except Exception:
            pass  # Continue even if deletion fails
    
    # Upload new image
    result = await upload_image(
        content,
        folder="sk8brigade/avatars",
        public_id=f"user_{current_user.id}"
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {result['error']}"
        )
    
    # Update user avatar URL
    await db.execute(
        update(User)
        .where(User.id == current_user.id)
        .values(avatar=result["url"])
    )
    await db.commit()
    
    return {
        "message": "Avatar uploaded successfully",
        "avatar_url": result["url"]
    }


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
    from app.models.user import Follow
    existing_follow = await db.execute(
        select(Follow).where(
            and_(
                Follow.follower_id == current_user.id,
                Follow.followed_id == user_id
            )
        )
    )
    
    if existing_follow.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already following this user"
        )
    
    # Create follow relationship
    follow = Follow(follower_id=current_user.id, followed_id=user_id)
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
        .values(follower_count=User.follower_count + 1)
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
    from app.models.user import Follow
    result = await db.execute(
        select(Follow).where(
            and_(
                Follow.follower_id == current_user.id,
                Follow.followed_id == user_id
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
        .values(follower_count=User.follower_count - 1)
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
    from app.models.user import Follow
    query = (
        select(User)
        .join(Follow, User.id == Follow.follower_id)
        .where(Follow.followed_id == user_id)
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
    from app.models.user import Follow
    query = (
        select(User)
        .join(Follow, User.id == Follow.followed_id)
        .where(Follow.follower_id == user_id)
        .offset(skip)
        .limit(limit)
    )
    
    result = await db.execute(query)
    following = result.scalars().all()
    
    return following