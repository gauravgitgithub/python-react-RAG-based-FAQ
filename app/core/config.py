from pydantic_settings import BaseSettings
from typing import Optional, Set
import os


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/rag_faq"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # File Upload
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: str = ".pdf,.txt"
    
    # Timeout settings
    UPLOAD_TIMEOUT: int = 600  # 10 minutes for file uploads
    PROCESSING_TIMEOUT: int = 300  # 5 minutes for document processing
    REQUEST_TIMEOUT: int = 300  # 5 minutes for general requests
    
    # FAISS
    FAISS_INDEX_PATH: str = "models/faiss_index"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # RAG
    TOP_K_CHUNKS: int = 5
    
    # Enhanced RAG settings
    MIN_SIMILARITY_THRESHOLD: float = 0.1  # Lowered for better retrieval
    MAX_CONTEXT_LENGTH: int = 4000
    ANSWER_MAX_LENGTH: int = 1000
    
    # LLM settings
    LLM_PROVIDER: str = "stubbed"  # "openai", "cohere", or "stubbed"
    OPENAI_API_KEY: Optional[str] = None
    COHERE_API_KEY: Optional[str] = None
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 500
    
    # Chunking settings
    CHUNK_MIN_SIZE: int = 100
    
    # Retrieval settings
    USE_SIMILARITY_FILTER: bool = True
    USE_QUESTION_CLASSIFICATION: bool = True
    
    @property
    def allowed_extensions_set(self) -> Set[str]:
        """Convert comma-separated extensions string to set"""
        return set(ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",") if ext.strip())
    
    @property
    def is_openai_available(self) -> bool:
        """Check if OpenAI is configured and available"""
        return self.LLM_PROVIDER == "openai" and bool(self.OPENAI_API_KEY)
    
    @property
    def is_cohere_available(self) -> bool:
        """Check if Cohere is configured and available"""
        return self.LLM_PROVIDER == "cohere" and bool(self.COHERE_API_KEY)
    
    @property
    def is_llm_available(self) -> bool:
        """Check if any LLM provider is available"""
        return self.is_openai_available or self.is_cohere_available
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.dirname(settings.FAISS_INDEX_PATH), exist_ok=True) 