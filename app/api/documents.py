from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_active_user, require_minimum_role
from app.models.user import User, UserRole
from app.schemas.document import Document, DocumentListResponse, DocumentUpdate, DocumentSelectionRequest
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=Document)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(require_minimum_role(UserRole.EDITOR)),
    db: AsyncSession = Depends(get_db)
):
    """Upload a new document"""
    document_service = DocumentService(db)
    return await document_service.upload_document(file, current_user)


@router.get("/", response_model=DocumentListResponse)
async def get_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get list of documents with optional filtering"""
    document_service = DocumentService(db)
    return await document_service.get_documents(skip=skip, limit=limit, is_active=is_active)


@router.get("/{document_id}", response_model=Document)
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific document by ID"""
    document_service = DocumentService(db)
    document = await document_service.get_document_by_id(document_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return document


@router.put("/{document_id}", response_model=Document)
async def update_document(
    document_id: int,
    document_update: DocumentUpdate,
    current_user: User = Depends(require_minimum_role(UserRole.EDITOR)),
    db: AsyncSession = Depends(get_db)
):
    """Update document metadata"""
    document_service = DocumentService(db)
    document = await document_service.update_document(document_id, document_update)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return document


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    current_user: User = Depends(require_minimum_role(UserRole.EDITOR)),
    db: AsyncSession = Depends(get_db)
):
    """Delete a document"""
    document_service = DocumentService(db)
    success = await document_service.delete_document(document_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return {"message": "Document deleted successfully"}


@router.post("/{document_id}/toggle-active", response_model=Document)
async def toggle_document_active(
    document_id: int,
    current_user: User = Depends(require_minimum_role(UserRole.EDITOR)),
    db: AsyncSession = Depends(get_db)
):
    """Toggle document active status"""
    document_service = DocumentService(db)
    document = await document_service.toggle_document_active(document_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return document


@router.post("/select-documents")
async def select_documents(
    selection_request: DocumentSelectionRequest,
    current_user: User = Depends(require_minimum_role(UserRole.EDITOR)),
    db: AsyncSession = Depends(get_db)
):
    """Select which documents are active for Q&A"""
    document_service = DocumentService(db)
    
    updated_documents = []
    for document_id in selection_request.document_ids:
        # Get document
        document = await document_service.get_document_by_id(document_id)
        if document:
            # Update active status
            document.is_active = selection_request.is_active
            await db.commit()
            await db.refresh(document)
            updated_documents.append(document)
    
    return {
        "message": f"Updated {len(updated_documents)} documents",
        "updated_documents": updated_documents
    }


@router.get("/{document_id}/chunks")
async def get_document_chunks(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all chunks for a document"""
    document_service = DocumentService(db)
    
    # Check if document exists
    document = await document_service.get_document_by_id(document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    chunks = await document_service.get_document_chunks(document_id)
    return {
        "document_id": document_id,
        "total_chunks": len(chunks),
        "chunks": chunks
    } 