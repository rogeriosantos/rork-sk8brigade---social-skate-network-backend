from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from uuid import UUID
import math

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.spot import Spot, SpotRating, SpotImage
from app.schemas.spot import (
    SpotResponse, SpotCreate, SpotUpdate, 
    SpotRatingCreate, SpotRatingResponse,
    SpotImageCreate, SpotImageResponse
)

router = APIRouter(prefix="/spots", tags=["spots"])


@router.get("/", response_model=List[SpotResponse])
async def get_spots(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = None,
    spot_type: Optional[str] = None,
    difficulty: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    radius_km: Optional[float] = Query(None, ge=0.1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get spots with optional filtering and location-based search"""
    query = select(Spot).where(Spot.is_public == True)
    
    if search:
        search_filter = or_(
            Spot.name.ilike(f"%{search}%"),
            Spot.description.ilike(f"%{search}%"),
            Spot.address.ilike(f"%{search}%")
        )
        query = query.where(search_filter)
    
    if spot_type:
        query = query.where(Spot.spot_type == spot_type)
    
    if difficulty:
        query = query.where(Spot.difficulty == difficulty)
    
    # Location-based filtering using Haversine formula approximation
    if latitude is not None and longitude is not None and radius_km is not None:
        # Convert km to degrees (rough approximation)
        lat_delta = radius_km / 111.0  # 1 degree lat ≈ 111 km
        lon_delta = radius_km / (111.0 * math.cos(math.radians(latitude)))
        
        query = query.where(
            and_(
                Spot.latitude.between(latitude - lat_delta, latitude + lat_delta),
                Spot.longitude.between(longitude - lon_delta, longitude + lon_delta)
            )
        )
    
    query = query.offset(skip).limit(limit).order_by(Spot.created_at.desc())
    
    result = await db.execute(query)
    spots = result.scalars().all()
    
    return spots


@router.get("/{spot_id}", response_model=SpotResponse)
async def get_spot(spot_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get spot by ID"""
    result = await db.execute(select(Spot).where(Spot.id == spot_id))
    spot = result.scalar_one_or_none()
    
    if not spot:
        raise HTTPException(status_code=404, detail="Spot not found")
    
    return spot


@router.post("/", response_model=SpotResponse)
async def create_spot(
    spot_data: SpotCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new spot"""
    db_spot = Spot(
        **spot_data.model_dump(),
        creator_id=current_user.id
    )
    
    db.add(db_spot)
    await db.commit()
    await db.refresh(db_spot)
    
    return db_spot


@router.put("/{spot_id}", response_model=SpotResponse)
async def update_spot(
    spot_id: UUID,
    spot_update: SpotUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a spot (only by creator)"""
    result = await db.execute(select(Spot).where(Spot.id == spot_id))
    spot = result.scalar_one_or_none()
    
    if not spot:
        raise HTTPException(status_code=404, detail="Spot not found")
    
    if spot.creator_id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="Only the spot creator can update this spot"
        )
    
    update_data = spot_update.model_dump(exclude_unset=True)
    
    if update_data:
        await db.execute(
            update(Spot)
            .where(Spot.id == spot_id)
            .values(**update_data)
        )
        await db.commit()
        await db.refresh(spot)
    
    return spot


@router.delete("/{spot_id}")
async def delete_spot(
    spot_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a spot (only by creator)"""
    result = await db.execute(select(Spot).where(Spot.id == spot_id))
    spot = result.scalar_one_or_none()
    
    if not spot:
        raise HTTPException(status_code=404, detail="Spot not found")
    
    if spot.creator_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only the spot creator can delete this spot"
        )
    
    await db.delete(spot)
    await db.commit()
    
    return {"message": "Spot deleted successfully"}


@router.post("/{spot_id}/ratings", response_model=SpotRatingResponse)
async def rate_spot(
    spot_id: UUID,
    rating_data: SpotRatingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Rate a spot"""
    # Check if spot exists
    spot_result = await db.execute(select(Spot).where(Spot.id == spot_id))
    spot = spot_result.scalar_one_or_none()
    
    if not spot:
        raise HTTPException(status_code=404, detail="Spot not found")
    
    # Validate rating
    if rating_data.rating < 1 or rating_data.rating > 5:
        raise HTTPException(
            status_code=400,
            detail="Rating must be between 1 and 5"
        )
    
    # Check if user already rated this spot
    existing_rating = await db.execute(
        select(SpotRating).where(
            and_(
                SpotRating.spot_id == spot_id,
                SpotRating.user_id == current_user.id
            )
        )
    )
    
    existing = existing_rating.scalar_one_or_none()
    
    if existing:
        # Update existing rating
        await db.execute(
            update(SpotRating)
            .where(SpotRating.id == existing.id)
            .values(
                rating=rating_data.rating,
                review=rating_data.review
            )
        )
        await db.commit()
        await db.refresh(existing)
        db_rating = existing
    else:
        # Create new rating
        db_rating = SpotRating(
            spot_id=spot_id,
            user_id=current_user.id,
            rating=rating_data.rating,
            review=rating_data.review
        )
        db.add(db_rating)
        await db.commit()
        await db.refresh(db_rating)
    
    # Update spot's average rating
    rating_stats = await db.execute(
        select(
            func.avg(SpotRating.rating),
            func.count(SpotRating.id)
        ).where(SpotRating.spot_id == spot_id)
    )
    
    avg_rating, count = rating_stats.first()
    
    await db.execute(
        update(Spot)
        .where(Spot.id == spot_id)
        .values(
            rating=float(avg_rating) if avg_rating else 0.0,
            rating_count=count
        )
    )
    await db.commit()
    
    return db_rating


@router.get("/{spot_id}/ratings", response_model=List[SpotRatingResponse])
async def get_spot_ratings(
    spot_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get ratings for a spot"""
    query = (
        select(SpotRating)
        .where(SpotRating.spot_id == spot_id)
        .offset(skip)
        .limit(limit)
        .order_by(SpotRating.created_at.desc())
    )
    
    result = await db.execute(query)
    ratings = result.scalars().all()
    
    return ratings


@router.post("/{spot_id}/images", response_model=SpotImageResponse)
async def add_spot_image(
    spot_id: UUID,
    image_data: SpotImageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add an image to a spot"""
    # Check if spot exists
    spot_result = await db.execute(select(Spot).where(Spot.id == spot_id))
    if not spot_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Spot not found")
    
    db_image = SpotImage(
        spot_id=spot_id,
        uploaded_by=current_user.id,
        **image_data.model_dump()
    )
    
    db.add(db_image)
    await db.commit()
    await db.refresh(db_image)
    
    return db_image


@router.get("/{spot_id}/images", response_model=List[SpotImageResponse])
async def get_spot_images(
    spot_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get images for a spot"""
    result = await db.execute(
        select(SpotImage)
        .where(SpotImage.spot_id == spot_id)
        .order_by(SpotImage.is_primary.desc(), SpotImage.created_at.desc())
    )
    
    images = result.scalars().all()
    return images