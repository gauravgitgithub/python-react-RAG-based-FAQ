from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.models.document import Document, DocumentChunk
from app.schemas.document import QuestionRequest, AnswerResponse, SourceChunk
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService


class QAService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.embedding_service = EmbeddingService()
        self.llm_service = LLMService()

    async def answer_question(self, question_request: QuestionRequest) -> AnswerResponse:
        """Answer a question using RAG approach with enhanced retrieval"""
        # Determine optimal top_k based on question type
        top_k = self._determine_top_k(question_request.question, question_request.top_k)
        
        # Search for relevant chunks
        similar_chunks = self.embedding_service.search_similar(
            question_request.question, 
            top_k
        )
        
        if not similar_chunks:
            return AnswerResponse(
                answer="I couldn't find any relevant information to answer your question.",
                sources=[],
                question=question_request.question
            )
        
        # Filter chunks by similarity threshold (lowered for better retrieval)
        filtered_chunks = self._filter_by_similarity(similar_chunks, threshold=0.1)
        
        if not filtered_chunks:
            # If no chunks pass the threshold, use the top 2 chunks anyway
            filtered_chunks = similar_chunks[:2]
        
        # Get chunk details from database
        source_chunks = await self._get_source_chunks(filtered_chunks)
        
        # Generate answer using LLM
        answer = await self._generate_answer(question_request.question, source_chunks)
        
        return AnswerResponse(
            answer=answer,
            sources=source_chunks,
            question=question_request.question
        )

    def _determine_top_k(self, question: str, user_top_k: Optional[int] = None) -> int:
        """Dynamically determine top_k based on question complexity"""
        if user_top_k:
            return user_top_k
            
        question_lower = question.lower()
        
        # Factual questions need less context
        if any(word in question_lower for word in ['what', 'who', 'when', 'where']):
            return 3
        # Explanatory questions need more context
        elif any(word in question_lower for word in ['how', 'why', 'explain', 'describe']):
            return 7
        # Procedural questions need detailed context
        elif any(word in question_lower for word in ['steps', 'procedure', 'process', 'guide']):
            return 8
        # Default
        else:
            return 5

    def _filter_by_similarity(self, chunks: List[tuple], threshold: float = 0.1) -> List[tuple]:
        """Filter chunks by similarity threshold (lowered default for better retrieval)"""
        return [(chunk_id, score) for chunk_id, score in chunks if score > threshold]

    async def _get_source_chunks(self, similar_chunks: List[tuple]) -> List[SourceChunk]:
        """Get detailed information about source chunks"""
        source_chunks = []
        
        for chunk_id, similarity_score in similar_chunks:
            # Parse chunk ID to get document_id and chunk_index
            try:
                doc_id_str, chunk_index_str = chunk_id.split("_")
                document_id = int(doc_id_str)
                chunk_index = int(chunk_index_str)
            except (ValueError, IndexError):
                continue
            
            # Get chunk from database
            result = await self.db.execute(
                select(DocumentChunk, Document.original_filename)
                .join(Document, DocumentChunk.document_id == Document.id)
                .where(
                    DocumentChunk.document_id == document_id,
                    DocumentChunk.chunk_index == chunk_index
                )
            )
            
            chunk_data = result.first()
            if chunk_data:
                chunk, document_name = chunk_data
                source_chunks.append(SourceChunk(
                    content=chunk.content,
                    document_name=document_name,
                    chunk_index=chunk.chunk_index,
                    similarity_score=similarity_score
                ))
        
        return source_chunks

    async def _generate_answer(self, question: str, source_chunks: List[SourceChunk]) -> str:
        """Generate answer using LLM with enhanced context"""
        if not source_chunks:
            return "I couldn't find any relevant information to answer your question."
        
        # Prepare enhanced context from source chunks
        context = self._prepare_enhanced_context(source_chunks)
        
        # Generate answer using LLM
        answer = await self.llm_service.generate_answer(question, context)
        
        return answer

    def _prepare_enhanced_context(self, source_chunks: List[SourceChunk]) -> str:
        """Prepare enhanced context string from source chunks with better formatting"""
        context_parts = []
        
        for i, chunk in enumerate(source_chunks, 1):
            # Simplified context format for better LLM compatibility
            context_parts.append(
                f"Source {i} (from {chunk.document_name}):\n"
                f"{chunk.content}\n"
            )
        
        return "\n".join(context_parts)

    async def get_qa_stats(self) -> dict:
        """Get statistics about the Q&A system"""
        # Get total documents
        doc_result = await self.db.execute(select(Document))
        total_documents = len(doc_result.scalars().all())
        
        # Get active documents
        active_doc_result = await self.db.execute(
            select(Document).where(Document.is_active == True)
        )
        active_documents = len(active_doc_result.scalars().all())
        
        # Get total chunks
        chunk_result = await self.db.execute(select(DocumentChunk))
        total_chunks = len(chunk_result.scalars().all())
        
        # Get FAISS index stats
        faiss_stats = self.embedding_service.get_index_stats()
        
        return {
            "total_documents": total_documents,
            "active_documents": active_documents,
            "total_chunks": total_chunks,
            "faiss_index": faiss_stats,
            "qa_config": {
                "llm_provider": settings.LLM_PROVIDER,
                "embedding_model": settings.EMBEDDING_MODEL,
                "chunk_size": settings.CHUNK_SIZE,
                "chunk_overlap": settings.CHUNK_OVERLAP,
                "top_k_chunks": settings.TOP_K_CHUNKS
            }
        } 