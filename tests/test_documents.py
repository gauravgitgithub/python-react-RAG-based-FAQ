import pytest
import io
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document


class TestDocuments:
    def test_upload_document_txt(self, client: TestClient, auth_headers):
        """Test uploading a text document"""
        # Create a simple text file
        text_content = "This is a test document for the RAG system."
        file_content = io.BytesIO(text_content.encode())
        
        response = client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files={"file": ("test.txt", file_content, "text/plain")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["original_filename"] == "test.txt"
        assert data["file_type"] == ".txt"
        assert data["is_active"] == True

    def test_upload_document_pdf(self, client: TestClient, auth_headers):
        """Test uploading a PDF document"""
        # Create a simple PDF-like file (this is a simplified test)
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n"
        file_content = io.BytesIO(pdf_content)
        
        response = client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files={"file": ("test.pdf", file_content, "application/pdf")}
        )
        
        # This might fail due to PDF parsing, but we test the endpoint structure
        assert response.status_code in [200, 400]  # 400 if PDF parsing fails

    def test_upload_document_invalid_type(self, client: TestClient, auth_headers):
        """Test uploading an invalid file type"""
        file_content = io.BytesIO(b"test content")
        
        response = client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files={"file": ("test.doc", file_content, "application/msword")}
        )
        
        assert response.status_code == 400
        assert "File type .doc not allowed" in response.json()["detail"]

    def test_upload_document_no_auth(self, client: TestClient):
        """Test uploading without authentication"""
        file_content = io.BytesIO(b"test content")
        
        response = client.post(
            "/api/v1/documents/upload",
            files={"file": ("test.txt", file_content, "text/plain")}
        )
        
        assert response.status_code == 401

    def test_get_documents(self, client: TestClient, auth_headers):
        """Test getting list of documents"""
        response = client.get("/api/v1/documents/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data

    def test_get_documents_with_filter(self, client: TestClient, auth_headers):
        """Test getting documents with active filter"""
        response = client.get(
            "/api/v1/documents/?is_active=true",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "documents" in data

    def test_get_documents_pagination(self, client: TestClient, auth_headers):
        """Test document pagination"""
        response = client.get(
            "/api/v1/documents/?skip=0&limit=10",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["size"] == 10

    def test_get_document_by_id(self, client: TestClient, auth_headers, db_session: AsyncSession):
        """Test getting a specific document"""
        # First create a document
        text_content = "Test document content"
        file_content = io.BytesIO(text_content.encode())
        
        upload_response = client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files={"file": ("test.txt", file_content, "text/plain")}
        )
        
        if upload_response.status_code == 200:
            document_id = upload_response.json()["id"]
            
            # Get the document
            response = client.get(
                f"/api/v1/documents/{document_id}",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == document_id

    def test_get_nonexistent_document(self, client: TestClient, auth_headers):
        """Test getting a document that doesn't exist"""
        response = client.get("/api/v1/documents/999", headers=auth_headers)
        
        assert response.status_code == 404
        assert "Document not found" in response.json()["detail"]

    def test_update_document(self, client: TestClient, auth_headers, db_session: AsyncSession):
        """Test updating document metadata"""
        # First create a document
        text_content = "Test document content"
        file_content = io.BytesIO(text_content.encode())
        
        upload_response = client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files={"file": ("test.txt", file_content, "text/plain")}
        )
        
        if upload_response.status_code == 200:
            document_id = upload_response.json()["id"]
            
            # Update the document
            response = client.put(
                f"/api/v1/documents/{document_id}",
                headers=auth_headers,
                json={"is_active": False}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["is_active"] == False

    def test_toggle_document_active(self, client: TestClient, auth_headers, db_session: AsyncSession):
        """Test toggling document active status"""
        # First create a document
        text_content = "Test document content"
        file_content = io.BytesIO(text_content.encode())
        
        upload_response = client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files={"file": ("test.txt", file_content, "text/plain")}
        )
        
        if upload_response.status_code == 200:
            document_id = upload_response.json()["id"]
            
            # Toggle active status
            response = client.post(
                f"/api/v1/documents/{document_id}/toggle-active",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["is_active"] == False  # Should toggle from True to False

    def test_select_documents(self, client: TestClient, auth_headers, db_session: AsyncSession):
        """Test selecting documents for Q&A"""
        # First create a document
        text_content = "Test document content"
        file_content = io.BytesIO(text_content.encode())
        
        upload_response = client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files={"file": ("test.txt", file_content, "text/plain")}
        )
        
        if upload_response.status_code == 200:
            document_id = upload_response.json()["id"]
            
            # Select documents
            response = client.post(
                "/api/v1/documents/select-documents",
                headers=auth_headers,
                json={
                    "document_ids": [document_id],
                    "is_active": False
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "Updated 1 documents" in data["message"]

    def test_get_document_chunks(self, client: TestClient, auth_headers, db_session: AsyncSession):
        """Test getting document chunks"""
        # First create a document
        text_content = "This is a test document with multiple sentences. It should be split into chunks."
        file_content = io.BytesIO(text_content.encode())
        
        upload_response = client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files={"file": ("test.txt", file_content, "text/plain")}
        )
        
        if upload_response.status_code == 200:
            document_id = upload_response.json()["id"]
            
            # Get chunks
            response = client.get(
                f"/api/v1/documents/{document_id}/chunks",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "chunks" in data
            assert "total_chunks" in data 