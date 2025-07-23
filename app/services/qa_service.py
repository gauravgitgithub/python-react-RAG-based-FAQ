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
        """Answer a question using RAG approach"""
        # Search for relevant chunks
        similar_chunks = self.embedding_service.search_similar(
            question_request.question, 
            question_request.top_k
        )
        
        if not similar_chunks:
            return AnswerResponse(
                answer="I couldn't find any relevant information to answer your question.",
                sources=[],
                question=question_request.question
            )
        
        # Get chunk details from database
        source_chunks = await self._get_source_chunks(similar_chunks)
        
        # Generate answer using LLM
        answer = await self._generate_answer(question_request.question, source_chunks)
        
        return AnswerResponse(
            answer=answer,
            sources=source_chunks,
            question=question_request.question
        )

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
        """Generate answer using LLM with context from source chunks"""
        if not source_chunks:
            return "I couldn't find any relevant information to answer your question."
        
        # Prepare context from source chunks
        context = self._prepare_context(source_chunks)
        
        # Generate answer using LLM
        answer = await self.llm_service.generate_answer(question, context)
        
        return answer

    def _prepare_context(self, source_chunks: List[SourceChunk]) -> str:
        """Prepare context string from source chunks"""
        context_parts = []
        
        for i, chunk in enumerate(source_chunks, 1):
            context_parts.append(
                f"Source {i} (from {chunk.document_name}, chunk {chunk.chunk_index}):\n"
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
            "faiss_index": faiss_stats
        } 