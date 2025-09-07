from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta

from app.core.database import get_db
from app.core.auth import authenticate_user, create_access_token, get_password_hash, get_current_user
from app.core.config import settings
from app.models.user import User, SkaterProfile, ShopProfile
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
        account_type=user_data.account_type
    )
    
    db.add(db_user)
    await db.flush()  # Flush to get the user ID
    
    # Create profile based on account type
    if user_data.account_type == "skater":
        skater_profile = SkaterProfile(
            user_id=db_user.id,
            setup={},
            skills=[],
            preferences={},
            joined_shops=[]
        )
        db.add(skater_profile)
    else:
        shop_profile = ShopProfile(
            user_id=db_user.id,
            name=user_data.display_name,
            brands=[]
        )
        db.add(shop_profile)
    
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
        from app.models.user import SkaterProfile, ShopProfile
        
        # Build basic response data with safe attribute access
        response_data = {
            "id": str(current_user.id),
            "username": getattr(current_user, 'username', ''),
            "email": getattr(current_user, 'email', ''),
            "display_name": getattr(current_user, 'display_name', ''),
            "bio": getattr(current_user, 'bio', None),
            "location": getattr(current_user, 'location', None),
            "account_type": getattr(current_user, 'account_type', ''),
            "avatar": getattr(current_user, 'avatar', None),
            "followers_count": getattr(current_user, 'followers_count', 0),
            "following_count": getattr(current_user, 'following_count', 0),
            "is_active": getattr(current_user, 'is_active', True),
            "is_verified": getattr(current_user, 'is_verified', False),
            "created_at": current_user.created_at.isoformat() if hasattr(current_user, 'created_at') and current_user.created_at else None,
            "skater_profile": None,
            "shop_profile": None
        }
        
        # Get skater profile if user is a skater
        if current_user.account_type == "skater":
            try:
                skater_result = await db.execute(
                    select(SkaterProfile).where(SkaterProfile.user_id == current_user.id)
                )
                skater_profile = skater_result.scalar_one_or_none()
                if skater_profile:
                    response_data["skater_profile"] = {
                        "setup": skater_profile.setup or {},
                        "skills": skater_profile.skills or [],
                        "preferences": skater_profile.preferences or {},
                        "joined_shops": skater_profile.joined_shops or []
                    }
            except Exception as profile_error:
                print(f"Error loading skater profile: {str(profile_error)}")
                response_data["skater_profile"] = {
                    "setup": {},
                    "skills": [],
                    "preferences": {},
                    "joined_shops": []
                }
        
        # Get shop profile if user is a skateshop
        elif current_user.account_type == "skateshop":
            try:
                shop_result = await db.execute(
                    select(ShopProfile).where(ShopProfile.user_id == current_user.id)
                )
                shop_profile = shop_result.scalar_one_or_none()
                if shop_profile:
                    response_data["shop_profile"] = {
                        "name": getattr(shop_profile, 'name', ''),
                        "description": getattr(shop_profile, 'description', ''),
                        "address": getattr(shop_profile, 'address', ''),
                        "phone": getattr(shop_profile, 'phone', ''),
                        "website": getattr(shop_profile, 'website', ''),
                        "brands": getattr(shop_profile, 'brands', [])
                    }
            except Exception as profile_error:
                print(f"Error loading shop profile: {str(profile_error)}")
                response_data["shop_profile"] = {
                    "name": "",
                    "description": "",
                    "address": "",
                    "phone": "",
                    "website": "",
                    "brands": []
                }
        
        return response_data
    
    except Exception as e:
        print(f"Error in get_current_user_info: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")