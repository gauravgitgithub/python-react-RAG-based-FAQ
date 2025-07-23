#!/usr/bin/env python3

import sys
import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

# Add current directory to path
sys.path.append('.')

from app.core.config import settings
from app.models.user import User
from app.models.document import Document

async def setup_user():
    """Check and create a default user if needed"""
    
    print("🔍 Checking database for users...")
    
    # Create database engine
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        # Check if users exist
        user_result = await db.execute(select(User))
        users = user_result.scalars().all()
        
        print(f"👥 Found {len(users)} users in database")
        
        if users:
            for user in users:
                print(f"  - ID: {user.id}, Email: {user.email}")
        else:
            print("❌ No users found. Creating default user...")
            
            # Create default user
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            
            default_user = User(
                email="admin@example.com",
                hashed_password=pwd_context.hash("admin123"),
                is_active=True
            )
            
            db.add(default_user)
            await db.commit()
            await db.refresh(default_user)
            
            print(f"✅ Created default user: {default_user.email}")
        
        # Check documents
        doc_result = await db.execute(select(Document))
        documents = doc_result.scalars().all()
        
        print(f"📚 Found {len(documents)} documents in database")
        
        for doc in documents:
            print(f"  - ID: {doc.id}, Filename: {doc.original_filename}")

if __name__ == "__main__":
    asyncio.run(setup_user()) 