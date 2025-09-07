from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta

from app.core.database import get_db
from app.core.auth import authenticate_user, create_access_token, get_password_hash, get_current_user
from app.core.config import settings
from app.models.user import User
from app.schemas.auth import UserLogin, UserRegister, Token
from app.schemas.user import UserFullResponse

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return access token"""
    user = await authenticate_user(db, user_credentials.username_or_email, user_credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=Token)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    """Register a new user"""
    # Check if username or email already exists
    existing_user = await db.execute(
        select(User).where((User.username == user_data.username) | (User.email == user_data.email))
    )
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Validate account type
    if user_data.account_type not in ["skater", "skateshop"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account type must be 'skater' or 'skateshop'"
        )
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        display_name=user_data.display_name,
        hashed_password=hashed_password,
        is_shop=(user_data.account_type == "skateshop")  # Convert to boolean for database
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(db_user.id)}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user information"""
    try:
        # Build response data with database field names
        response_data = {
            "id": str(current_user.id),
            "username": getattr(current_user, 'username', ''),
            "email": getattr(current_user, 'email', ''),
            "display_name": getattr(current_user, 'display_name', ''),
            "bio": getattr(current_user, 'bio', None),
            "is_shop": getattr(current_user, 'is_shop', False),
            "profile_picture": getattr(current_user, 'profile_picture', None),
            "follower_count": getattr(current_user, 'follower_count', 0),
            "following_count": getattr(current_user, 'following_count', 0),
            "is_active": getattr(current_user, 'is_active', True),
            "is_verified": getattr(current_user, 'is_verified', False),
            "created_at": getattr(current_user, 'created_at', None),
        }
        
        # Get skate setups if not a shop
        if not current_user.is_shop:
            from app.models.user import SkateSetup
            setups_result = await db.execute(
                select(SkateSetup).where(SkateSetup.user_id == current_user.id)
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
    
    except Exception as e:
        print(f"Error in get_current_user_info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user information: {str(e)}"
        )
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")