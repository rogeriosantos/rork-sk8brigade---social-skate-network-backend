#!/usr/bin/env python3

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

async def inspect_users_table():
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
    
    print(f"Connecting to: {database_url}")
    
    try:
        # Connect to database
        conn = await asyncpg.connect(database_url)
        
        # Query to get all columns in users table
        query = """
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = 'users' 
        AND table_schema = 'public'
        ORDER BY ordinal_position;
        """
        
        rows = await conn.fetch(query)
        
        print("Actual columns in users table:")
        print("=" * 50)
        for row in rows:
            print(f"Column: {row['column_name']}")
            print(f"  Type: {row['data_type']}")
            print(f"  Nullable: {row['is_nullable']}")
            print(f"  Default: {row['column_default']}")
            print()
        
        # Also check if profile_picture exists specifically
        check_query = """
        SELECT EXISTS (
            SELECT 1 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name = 'profile_picture'
            AND table_schema = 'public'
        );
        """
        
        exists = await conn.fetchval(check_query)
        print(f"profile_picture column exists: {exists}")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error inspecting database: {e}")

if __name__ == "__main__":
    asyncio.run(inspect_users_table())
