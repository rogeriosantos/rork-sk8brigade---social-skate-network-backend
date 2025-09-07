import cloudinary
import cloudinary.uploader
from app.core.config import settings

# Configure Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)


async def upload_image(file_content: bytes, folder: str = "sk8brigade", public_id: str = None) -> dict:
    """Upload image to Cloudinary"""
    try:
        result = cloudinary.uploader.upload(
            file_content,
            folder=folder,
            public_id=public_id,
            overwrite=True,
            resource_type="image",
            format="webp",  # Convert to WebP for better compression
            quality="auto",  # Automatic quality optimization
            fetch_format="auto"  # Automatic format selection
        )
        return {
            "success": True,
            "url": result.get("secure_url"),
            "public_id": result.get("public_id")
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def delete_image(public_id: str) -> dict:
    """Delete image from Cloudinary"""
    try:
        result = cloudinary.uploader.destroy(public_id)
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
