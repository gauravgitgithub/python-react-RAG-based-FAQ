#!/usr/bin/env python3
"""
Test script to verify RAG-based FAQ System setup
"""

import asyncio
import sys
import os
from pathlib import Path

def test_imports():
    """Test if all required packages can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import fastapi
        print("✅ FastAPI imported successfully")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        import sqlalchemy
        print("✅ SQLAlchemy imported successfully")
    except ImportError as e:
        print(f"❌ SQLAlchemy import failed: {e}")
        return False
    
    try:
        import faiss
        print("✅ FAISS imported successfully")
    except ImportError as e:
        print(f"❌ FAISS import failed: {e}")
        return False
    
    try:
        import sentence_transformers
        print("✅ Sentence Transformers imported successfully")
    except ImportError as e:
        print(f"❌ Sentence Transformers import failed: {e}")
        return False
    
    try:
        import redis
        print("✅ Redis imported successfully")
    except ImportError as e:
        print(f"❌ Redis import failed: {e}")
        return False
    
    return True

def test_app_imports():
    """Test if app modules can be imported"""
    print("\n🔍 Testing app imports...")
    
    try:
        from app.core.config import settings
        print("✅ App config imported successfully")
    except ImportError as e:
        print(f"❌ App config import failed: {e}")
        return False
    
    try:
        from app.models.user import User, UserRole
        print("✅ User models imported successfully")
    except ImportError as e:
        print(f"❌ User models import failed: {e}")
        return False
    
    try:
        from app.services.auth_service import AuthService
        print("✅ Auth service imported successfully")
    except ImportError as e:
        print(f"❌ Auth service import failed: {e}")
        return False
    
    try:
        from app.services.embedding_service import EmbeddingService
        print("✅ Embedding service imported successfully")
    except ImportError as e:
        print(f"❌ Embedding service import failed: {e}")
        return False
    
    return True

def test_directories():
    """Test if required directories exist"""
    print("\n🔍 Testing directories...")
    
    required_dirs = ["uploads", "models"]
    
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✅ Directory '{dir_name}' exists")
        else:
            print(f"⚠️  Directory '{dir_name}' doesn't exist (will be created)")
            try:
                os.makedirs(dir_name, exist_ok=True)
                print(f"✅ Created directory '{dir_name}'")
            except Exception as e:
                print(f"❌ Failed to create directory '{dir_name}': {e}")
                return False
    
    return True

def test_environment():
    """Test environment variables"""
    print("\n🔍 Testing environment...")
    
    # Set default values for testing
    os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost:5432/rag_faq")
    os.environ.setdefault("REDIS_URL", "redis://localhost:6379")
    os.environ.setdefault("SECRET_KEY", "test-secret-key")
    
    try:
        from app.core.config import settings
        print("✅ Configuration loaded successfully")
        print(f"   - Database URL: {settings.DATABASE_URL}")
        print(f"   - Redis URL: {settings.REDIS_URL}")
        print(f"   - Embedding Model: {settings.EMBEDDING_MODEL}")
        print(f"   - Chunk Size: {settings.CHUNK_SIZE}")
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False
    
    return True

async def test_services():
    """Test service initialization"""
    print("\n🔍 Testing services...")
    
    try:
        from app.services.embedding_service import EmbeddingService
        embedding_service = EmbeddingService()
        print("✅ Embedding service initialized successfully")
    except Exception as e:
        print(f"❌ Embedding service initialization failed: {e}")
        return False
    
    try:
        from app.utils.text_chunker import TextChunker
        chunker = TextChunker()
        print("✅ Text chunker initialized successfully")
    except Exception as e:
        print(f"❌ Text chunker initialization failed: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 RAG-based FAQ System Setup Test")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed. Please install missing dependencies.")
        sys.exit(1)
    
    # Test app imports
    if not test_app_imports():
        print("\n❌ App import tests failed. Check the application structure.")
        sys.exit(1)
    
    # Test directories
    if not test_directories():
        print("\n❌ Directory tests failed.")
        sys.exit(1)
    
    # Test environment
    if not test_environment():
        print("\n❌ Environment tests failed.")
        sys.exit(1)
    
    # Test services
    if not asyncio.run(test_services()):
        print("\n❌ Service tests failed.")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✅ All tests passed! The system is ready to use.")
    print("\n📖 Next steps:")
    print("   1. Set up your database (PostgreSQL)")
    print("   2. Set up Redis")
    print("   3. Configure environment variables")
    print("   4. Run: uvicorn app.main:app --reload")
    print("   5. Visit: http://localhost:8000/docs")

if __name__ == "__main__":
    main() 