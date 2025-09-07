#!/usr/bin/env python3

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

async def test_direct_db_auth():
    # Load environment variables
    load_dotenv()
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL not found in environment variables")
        return
    
    # Convert SQLAlchemy URL to asyncpg format
    if database_url.startswith("postgresql+asyncpg://"):
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    
    try:
        # Connect to database
        conn = await asyncpg.connect(database_url)
        
        # Test direct query to find user "dois"
        query = """
        SELECT id, username, email, hashed_password, display_name, bio, 
               profile_picture, is_shop, is_active, is_verified, 
               follower_count, following_count, created_at, updated_at
        FROM users 
        WHERE username = $1 OR email = $1
        """
        
        row = await conn.fetchrow(query, "dois")
        
        if row:
            print("User found in database:")
            print(f"  ID: {row['id']}")
            print(f"  Username: {row['username']}")
            print(f"  Email: {row['email']}")
            print(f"  Display Name: {row['display_name']}")
            print(f"  Is Shop: {row['is_shop']}")
            print(f"  Is Active: {row['is_active']}")
            print(f"  Password Hash: {row['hashed_password'][:50]}...")
            
            # Test password verification
            import bcrypt
            test_password = "Com,,320"
            hashed = row['hashed_password'].encode('utf-8')
            
            if bcrypt.checkpw(test_password.encode('utf-8'), hashed):
                print("✓ Password verification successful!")
            else:
                print("❌ Password verification failed!")
        else:
            print("❌ User 'dois' not found in database")
        
        await conn.close()
        
    except Exception as e:
        print(f"Database error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_direct_db_auth())
