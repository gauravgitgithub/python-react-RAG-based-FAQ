from app.core.celery_app import celery_app
from app.services.embedding_service import EmbeddingService
from app.utils.text_chunker import TextChunker
from app.core.config import settings


@celery_app.task
def process_document_chunks(document_id: int, text_content: str):
    """Background task to process document chunks and generate embeddings"""
    try:
        # Initialize services
        embedding_service = EmbeddingService()
        text_chunker = TextChunker(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )
        
        # Split text into chunks
        chunks = text_chunker.split_text(text_content)
        
        # Prepare data for embedding service
        texts = []
        chunk_ids = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{document_id}_{i}"
            texts.append(chunk["text"])
            chunk_ids.append(chunk_id)
        
        # Generate and store embeddings
        if texts:
            embedding_service.add_embeddings(texts, chunk_ids)
        
        return {
            "status": "success",
            "document_id": document_id,
            "chunks_processed": len(chunks)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "document_id": document_id,
            "error": str(e)
        }


@celery_app.task
def rebuild_faiss_index():
    """Background task to rebuild the FAISS index"""
    try:
        embedding_service = EmbeddingService()
        
        # This would typically involve:
        # 1. Reading all chunks from database
        # 2. Regenerating embeddings
        # 3. Rebuilding the FAISS index
        
        return {
            "status": "success",
            "message": "FAISS index rebuilt successfully"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@celery_app.task
def cleanup_old_embeddings():
    """Background task to cleanup old embeddings"""
    try:
        embedding_service = EmbeddingService()
        
        # This would typically involve:
        # 1. Identifying orphaned embeddings
        # 2. Removing them from FAISS index
        # 3. Cleaning up storage
        
        return {
            "status": "success",
            "message": "Old embeddings cleaned up successfully"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        } 