#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_backend():
    try:
        print("Testing backend imports...")
        from app.main import app
        print("✅ Backend app imported successfully")
        
        print("Testing database connection...")
        from app.core.database import engine
        async with engine.begin() as conn:
            await conn.run_sync(lambda sync_conn: sync_conn.execute("SELECT 1"))
        print("✅ Database connection successful")
        
        print("Testing configuration...")
        from app.core.config import settings
        print(f"✅ Configuration loaded: DATABASE_URL={settings.DATABASE_URL[:50]}...")
        
        print("✅ All backend tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_backend())
    sys.exit(0 if success else 1) 