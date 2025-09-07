#!/usr/bin/env python3

try:
    print("Testing User model import...")
    from app.models.user import User
    print("✓ User model imported successfully")
    
    print("Testing database connection...")
    from app.core.database import get_db
    print("✓ Database module imported successfully")
    
    print("Testing auth module...")
    from app.core.auth import authenticate_user
    print("✓ Auth module imported successfully")
    
    print("All imports successful!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
