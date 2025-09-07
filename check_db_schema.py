#!/usr/bin/env python3
"""
Quick database schema check script
"""
import asyncio
from sqlalchemy import text
from app.core.database import get_db

async def check_users_table():
    """Check the actual structure of the users table"""
    try:
        # Get database session
        async for db in get_db():
            # Check table structure
            result = await db.execute(text("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                ORDER BY ordinal_position;
            """))
            
            print("Users table structure:")
            for row in result.fetchall():
                print(f"  {row.column_name}: {row.data_type} ({'NULL' if row.is_nullable == 'YES' else 'NOT NULL'})")
            
            # Check if skate_setups table exists
            result = await db.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE '%setup%';
            """))
            
            print("\nSetup-related tables:")
            setup_tables = result.fetchall()
            if setup_tables:
                for row in setup_tables:
                    print(f"  {row.table_name}")
            else:
                print("  No setup tables found")
            
            break
    except Exception as e:
        print(f"Error checking table structure: {e}")

if __name__ == "__main__":
    asyncio.run(check_users_table())
