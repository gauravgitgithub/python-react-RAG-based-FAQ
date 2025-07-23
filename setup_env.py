#!/usr/bin/env python3

import os
import sys
import shutil

def create_env_file():
    """Create a .env file from .env.example template"""
    
    # Check if .env.example exists
    if not os.path.exists('.env.example'):
        print("❌ .env.example file not found!")
        print("💡 Please ensure .env.example exists in the project root.")
        return
    
    # Check if .env already exists
    if os.path.exists('.env'):
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("❌ Setup cancelled.")
            return
    
    try:
        # Copy .env.example to .env
        shutil.copy('.env.example', '.env')
        
        print("✅ .env file created successfully from .env.example!")
        print("\n📝 Next steps:")
        print("1. Edit the .env file with your actual values")
        print("2. Set your API keys:")
        print("   - OPENAI_API_KEY: Get from https://platform.openai.com/api-keys")
        print("   - COHERE_API_KEY: Get from https://dashboard.cohere.ai/api-keys")
        print("3. Choose your LLM provider:")
        print("   - LLM_PROVIDER=openai (for OpenAI)")
        print("   - LLM_PROVIDER=cohere (for Cohere)")
        print("   - LLM_PROVIDER=stubbed (for testing)")
        print("4. Update database and Redis URLs if needed")
        print("5. Change SECRET_KEY for production")
        print("6. Run 'python3 validate_config.py' to validate your configuration")
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return

def show_env_help():
    """Show help information about environment variables"""
    
    help_content = """
🔧 Environment Variables Guide

📊 Database & Redis:
- DATABASE_URL: PostgreSQL connection string
- REDIS_URL: Redis connection string

🔐 Security:
- SECRET_KEY: JWT secret key (change in production!)
- ALGORITHM: JWT algorithm (default: HS256)
- ACCESS_TOKEN_EXPIRE_MINUTES: Token expiry time

📁 File Upload:
- UPLOAD_DIR: Directory for uploaded files
- MAX_FILE_SIZE: Maximum file size in bytes (default: 10MB)
- ALLOWED_EXTENSIONS: Comma-separated file extensions

🤖 AI & ML:
- EMBEDDING_MODEL: Sentence transformer model
- CHUNK_SIZE: Text chunk size in characters
- CHUNK_OVERLAP: Overlap between chunks
- FAISS_INDEX_PATH: Path for FAISS index files

🎯 RAG Settings:
- TOP_K_CHUNKS: Number of chunks to retrieve
- MIN_SIMILARITY_THRESHOLD: Minimum similarity score (0.0-1.0)
- MAX_CONTEXT_LENGTH: Maximum context length for LLM
- ANSWER_MAX_LENGTH: Maximum answer length

🧠 LLM Configuration:
- LLM_PROVIDER: "openai", "cohere", or "stubbed"
- OPENAI_API_KEY: Your OpenAI API key
- COHERE_API_KEY: Your Cohere API key
- LLM_TEMPERATURE: Creativity level (0.0-1.0)
- LLM_MAX_TOKENS: Maximum tokens for responses

⚙️ Advanced Settings:
- USE_SIMILARITY_FILTER: Enable/disable similarity filtering
- USE_QUESTION_CLASSIFICATION: Enable/disable question classification
- CHUNK_MIN_SIZE: Minimum chunk size

💡 Tips:
- Use "stubbed" provider for testing without API keys
- Lower temperature (0.3) for factual answers
- Higher temperature (0.7-0.9) for creative answers
- Adjust chunk size based on your document types
- Fine-tune similarity threshold based on answer quality
- Check .env.example for detailed configuration options
"""
    
    print(help_content)

def show_quick_start():
    """Show quick start guide"""
    
    quick_start = """
🚀 Quick Start Guide

1. Create .env file:
   python3 setup_env.py

2. Configure your settings in .env:
   - Set LLM_PROVIDER (openai/cohere/stubbed)
   - Add API keys if using OpenAI or Cohere
   - Update database URLs if needed

3. Validate configuration:
   python3 validate_config.py

4. Start the system:
   ./start.sh

5. Access the application:
   - Frontend: http://localhost:3001
   - API Docs: http://localhost:8000/docs

📚 For detailed configuration options, see .env.example
🔧 For help with environment variables, run: python3 setup_env.py help
"""
    
    print(quick_start)

def main():
    """Main function"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "help":
            show_env_help()
        elif sys.argv[1] == "quickstart":
            show_quick_start()
        else:
            print("Usage: python3 setup_env.py [help|quickstart]")
            print("  help      - Show environment variables guide")
            print("  quickstart - Show quick start guide")
    else:
        create_env_file()

if __name__ == "__main__":
    main() 