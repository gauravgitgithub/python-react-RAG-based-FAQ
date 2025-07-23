import os
import uuid
import asyncio
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from fastapi import UploadFile, HTTPException, status
import PyPDF2
import io

from app.core.config import settings
from app.models.document import Document as DocumentModel, DocumentChunk as DocumentChunkModel
from app.models.user import User
from app.schemas.document import Document, DocumentCreate, DocumentUpdate, DocumentListResponse, DocumentChunk
from app.services.embedding_service import EmbeddingService
from app.utils.text_chunker import TextChunker


class DocumentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.embedding_service = EmbeddingService()
        self.text_chunker = TextChunker(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )

    async def upload_document(self, file: UploadFile, user: User) -> Document:
        """Upload and process a document with timeout handling"""
        try:
            # Validate file type
            file_extension = os.path.splitext(file.filename)[1].lower()
            if file_extension not in settings.allowed_extensions_set:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File type {file_extension} not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}"
                )
            
            # Validate file size
            if file.size and file.size > settings.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File size {file.size} exceeds maximum allowed size {settings.MAX_FILE_SIZE}"
                )
            
            # Generate unique filename
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
            
            # Save file with timeout
            content = await asyncio.wait_for(file.read(), timeout=settings.UPLOAD_TIMEOUT)
            with open(file_path, "wb") as f:
                f.write(content)
            
            # Extract text from document with timeout
            text_content = await asyncio.wait_for(
                self._extract_text(file_path, file_extension), 
                timeout=settings.PROCESSING_TIMEOUT
            )
            
            # Create document record
            document = DocumentModel(
                filename=unique_filename,
                original_filename=file.filename,
                file_path=file_path,
                file_size=len(content),
                file_type=file_extension,
                uploaded_by=user.id
            )
            
            self.db.add(document)
            await self.db.commit()
            await self.db.refresh(document)
            
            # Process document chunks and embeddings with timeout
            await asyncio.wait_for(
                self._process_document_chunks(document, text_content),
                timeout=settings.PROCESSING_TIMEOUT
            )
            
            # Convert to Pydantic schema
            return Document.model_validate(document)
            
        except asyncio.TimeoutError:
            # Clean up any partial uploads
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail="Document processing timed out. Please try with a smaller file or try again later."
            )
        except Exception as e:
            # Clean up any partial uploads
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing document: {str(e)}"
            )

    async def _extract_text(self, file_path: str, file_extension: str) -> str:
        """Extract text from different file types"""
        if file_extension == ".pdf":
            return await asyncio.to_thread(self._extract_pdf_text, file_path)
        elif file_extension == ".txt":
            return await asyncio.to_thread(self._extract_txt_text, file_path)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {file_extension}"
            )

    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error extracting text from PDF: {str(e)}"
            )

    def _extract_txt_text(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error reading text file: {str(e)}"
            )

    async def _process_document_chunks(self, document: DocumentModel, text_content: str):
        """Process document text into chunks and generate embeddings with timeout handling"""
        # Split text into chunks
        chunks = await asyncio.to_thread(self.text_chunker.split_text, text_content)
        
        # Prepare data for embedding service
        texts = []
        chunk_ids = []
        
        for i, chunk in enumerate(chunks):
            # Create chunk record
            chunk_id = f"{document.id}_{i}"
            db_chunk = DocumentChunkModel(
                document_id=document.id,
                chunk_index=i,
                content=chunk["text"],
                start_char=chunk["start"],
                end_char=chunk["end"],
                embedding_id=chunk_id
            )
            
            self.db.add(db_chunk)
            texts.append(chunk["text"])
            chunk_ids.append(chunk_id)
        
        # Commit chunks to database
        await self.db.commit()
        
        # Generate and store embeddings with timeout
        await asyncio.wait_for(
            asyncio.to_thread(self.embedding_service.add_embeddings, texts, chunk_ids),
            timeout=settings.PROCESSING_TIMEOUT
        )

    async def get_documents(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        is_active: Optional[bool] = None
    ) -> DocumentListResponse:
        """Get list of documents with optional filtering"""
        query = select(DocumentModel)
        
        if is_active is not None:
            query = query.where(DocumentModel.is_active == is_active)
        
        # Get total count
        count_query = select(DocumentModel)
        if is_active is not None:
            count_query = count_query.where(DocumentModel.is_active == is_active)
        
        total_result = await self.db.execute(count_query)
        total = len(total_result.scalars().all())
        
        # Get paginated results
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        documents = result.scalars().all()
        
        # Convert to Pydantic schemas
        document_schemas = [Document.model_validate(doc) for doc in documents]
        
        return DocumentListResponse(
            documents=document_schemas,
            total=total,
            page=skip // limit + 1,
            size=len(document_schemas)
        )

    async def get_document_by_id(self, document_id: int) -> Optional[Document]:
        """Get document by ID"""
        result = await self.db.execute(
            select(DocumentModel).where(DocumentModel.id == document_id)
        )
        document = result.scalar_one_or_none()
        if document:
            return Document.model_validate(document)
        return None

    async def update_document(self, document_id: int, document_update: DocumentUpdate) -> Optional[Document]:
        """Update document"""
        result = await self.db.execute(
            select(DocumentModel).where(DocumentModel.id == document_id)
        )
        document = result.scalar_one_or_none()
        
        if not document:
            return None
        
        # Prepare update data
        update_data = {}
        if document_update.is_active is not None:
            update_data["is_active"] = document_update.is_active
        
        if update_data:
            await self.db.execute(
                update(DocumentModel)
                .where(DocumentModel.id == document_id)
                .values(**update_data)
            )
            await self.db.commit()
            await self.db.refresh(document)
        
        return Document.model_validate(document)

    async def delete_document(self, document_id: int) -> bool:
        """Delete document and its chunks"""
        result = await self.db.execute(
            select(DocumentModel).where(DocumentModel.id == document_id)
        )
        document = result.scalar_one_or_none()
        
        if not document:
            return False
        
        # Delete chunks from FAISS index
        chunks_result = await self.db.execute(
            select(DocumentChunkModel).where(DocumentChunkModel.document_id == document_id)
        )
        chunks = chunks_result.scalars().all()
        
        chunk_ids = [chunk.embedding_id for chunk in chunks]
        if chunk_ids:
            self.embedding_service.remove_embeddings(chunk_ids)
        
        # Delete chunks from database
        await self.db.execute(
            select(DocumentChunkModel).where(DocumentChunkModel.document_id == document_id)
        )
        
        # Delete document file
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        # Delete document record
        await self.db.delete(document)
        await self.db.commit()
        
        return True

    async def get_document_chunks(self, document_id: int) -> List[DocumentChunk]:
        """Get chunks for a specific document"""
        result = await self.db.execute(
            select(DocumentChunkModel).where(DocumentChunkModel.document_id == document_id)
        )
        chunks = result.scalars().all()
        return [DocumentChunk.model_validate(chunk) for chunk in chunks]

    async def toggle_document_active(self, document_id: int) -> Optional[Document]:
        """Toggle document active status"""
        result = await self.db.execute(
            select(DocumentModel).where(DocumentModel.id == document_id)
        )
        document = result.scalar_one_or_none()
        
        if not document:
            return None
        
        document.is_active = not document.is_active
        await self.db.commit()
        await self.db.refresh(document)
        
        return Document.model_validate(document) 