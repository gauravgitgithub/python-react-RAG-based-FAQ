#!/usr/bin/env python3

import os
import sys
from pathlib import Path

def validate_env_file():
    """Validate the .env file and configuration"""
    
    print("🔍 Validating Configuration...")
    print("=" * 50)
    
    # Check if .env file exists
    if not Path('.env').exists():
        print("❌ .env file not found!")
        print("💡 Run 'python3 setup_env.py' to create it.")
        return False
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Required variables
    required_vars = [
        'DATABASE_URL',
        'REDIS_URL', 
        'SECRET_KEY',
        'LLM_PROVIDER'
    ]
    
    # Optional but important variables
    optional_vars = [
        'OPENAI_API_KEY',
        'COHERE_API_KEY',
        'EMBEDDING_MODEL',
        'CHUNK_SIZE',
        'CHUNK_OVERLAP',
        'TOP_K_CHUNKS'
    ]
    
    print("📋 Checking required variables:")
    missing_required = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'SECRET' in var or 'KEY' in var:
                display_value = value[:8] + "..." if len(value) > 8 else "***"
            else:
                display_value = value
            print(f"  ✅ {var}: {display_value}")
        else:
            print(f"  ❌ {var}: Not set")
            missing_required.append(var)
    
    print("\n📋 Checking optional variables:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'KEY' in var:
                display_value = value[:8] + "..." if len(value) > 8 else "***"
            else:
                display_value = value
            print(f"  ✅ {var}: {display_value}")
        else:
            print(f"  ⚠️  {var}: Not set (using default)")
    
    # Check LLM provider configuration
    print("\n🧠 LLM Provider Configuration:")
    llm_provider = os.getenv('LLM_PROVIDER', 'stubbed')
    print(f"  Provider: {llm_provider}")
    
    if llm_provider == 'openai':
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            print("  ✅ OpenAI API key is set")
        else:
            print("  ❌ OpenAI API key is missing")
            missing_required.append('OPENAI_API_KEY')
    
    elif llm_provider == 'cohere':
        cohere_key = os.getenv('COHERE_API_KEY')
        if cohere_key:
            print("  ✅ Cohere API key is set")
        else:
            print("  ❌ Cohere API key is missing")
            missing_required.append('COHERE_API_KEY')
    
    elif llm_provider == 'stubbed':
        print("  ℹ️  Using stubbed provider (no API key needed)")
    
    else:
        print(f"  ❌ Unknown LLM provider: {llm_provider}")
        print("  Valid options: openai, cohere, stubbed")
        missing_required.append('LLM_PROVIDER')
    
    # Check file extensions
    print("\n📁 File Upload Configuration:")
    allowed_extensions = os.getenv('ALLOWED_EXTENSIONS', '.pdf,.txt')
    print(f"  Allowed extensions: {allowed_extensions}")
    
    # Check chunking settings
    print("\n📏 Chunking Configuration:")
    chunk_size = os.getenv('CHUNK_SIZE', '1000')
    chunk_overlap = os.getenv('CHUNK_OVERLAP', '200')
    print(f"  Chunk size: {chunk_size}")
    print(f"  Chunk overlap: {chunk_overlap}")
    
    # Check RAG settings
    print("\n🎯 RAG Configuration:")
    top_k = os.getenv('TOP_K_CHUNKS', '5')
    similarity_threshold = os.getenv('MIN_SIMILARITY_THRESHOLD', '0.3')
    print(f"  Top K chunks: {top_k}")
    print(f"  Similarity threshold: {similarity_threshold}")
    
    # Summary
    print("\n" + "=" * 50)
    if missing_required:
        print("❌ Configuration validation failed!")
        print(f"Missing required variables: {', '.join(missing_required)}")
        return False
    else:
        print("✅ Configuration validation passed!")
        print("🚀 Your system is ready to run!")
        return True

def test_imports():
    """Test if all required packages can be imported"""
    
    print("\n🔍 Testing package imports...")
    
    packages = [
        'fastapi',
        'uvicorn', 
        'sqlalchemy',
        'faiss',
        'sentence_transformers',
        'openai',
        'cohere',
        'pydantic',
        'pydantic_settings'
    ]
    
    failed_imports = []
    
    for package in packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError as e:
            print(f"  ❌ {package}: {e}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        print("💡 Run 'pip install -r requirements.txt' to install missing packages")
        return False
    else:
        print("\n✅ All packages imported successfully!")
        return True

def test_config_loading():
    """Test if the configuration can be loaded properly"""
    
    print("\n🔍 Testing configuration loading...")
    
    try:
        # Add current directory to path
        sys.path.insert(0, '.')
        
        # Import and test configuration
        from app.core.config import settings
        
        print(f"  ✅ Database URL: {settings.DATABASE_URL}")
        print(f"  ✅ LLM Provider: {settings.LLM_PROVIDER}")
        print(f"  ✅ Embedding Model: {settings.EMBEDDING_MODEL}")
        print(f"  ✅ Chunk Size: {settings.CHUNK_SIZE}")
        print(f"  ✅ Allowed Extensions: {settings.allowed_extensions_set}")
        
        # Test LLM availability
        print(f"  ✅ OpenAI Available: {settings.is_openai_available}")
        print(f"  ✅ Cohere Available: {settings.is_cohere_available}")
        print(f"  ✅ Any LLM Available: {settings.is_llm_available}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Configuration loading failed: {e}")
        return False

def main():
    """Main validation function"""
    
    print("🔧 RAG-based FAQ System Configuration Validator")
    print("=" * 60)
    
    # Test imports first
    imports_ok = test_imports()
    
    # Test configuration loading
    config_ok = test_config_loading()
    
    # Validate environment variables
    env_ok = validate_env_file()
    
    print("\n" + "=" * 60)
    print("📊 Validation Summary:")
    print(f"  Package Imports: {'✅' if imports_ok else '❌'}")
    print(f"  Configuration Loading: {'✅' if config_ok else '❌'}")
    print(f"  Environment Variables: {'✅' if env_ok else '❌'}")
    
    if imports_ok and config_ok and env_ok:
        print("\n🎉 All validations passed! Your system is ready to run.")
        print("💡 Run './start.sh' to start the system.")
    else:
        print("\n⚠️  Some validations failed. Please fix the issues above.")
        print("💡 Check the error messages for guidance.")

if __name__ == "__main__":
    main() 