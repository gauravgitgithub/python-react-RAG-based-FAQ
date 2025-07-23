import pytest
import io
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestQA:
    def test_ask_question_no_documents(self, client: TestClient, auth_headers):
        """Test asking a question when no documents are available"""
        response = client.post(
            "/api/v1/qa/ask",
            headers=auth_headers,
            json={
                "question": "What is the capital of France?",
                "top_k": 5
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "sources" in data
        assert "question" in data
        # Should return a default answer when no documents are available
        assert "couldn't find any relevant information" in data["answer"].lower()

    def test_ask_question_with_documents(self, client: TestClient, auth_headers, db_session: AsyncSession):
        """Test asking a question with documents available"""
        # First upload a document
        text_content = "Paris is the capital of France. It is a beautiful city known for the Eiffel Tower."
        file_content = io.BytesIO(text_content.encode())
        
        upload_response = client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files={"file": ("test.txt", file_content, "text/plain")}
        )
        
        if upload_response.status_code == 200:
            # Ask a question
            response = client.post(
                "/api/v1/qa/ask",
                headers=auth_headers,
                json={
                    "question": "What is the capital of France?",
                    "top_k": 3
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "answer" in data
            assert "sources" in data
            assert "question" in data
            assert data["question"] == "What is the capital of France?"

    def test_ask_question_custom_top_k(self, client: TestClient, auth_headers, db_session: AsyncSession):
        """Test asking a question with custom top_k parameter"""
        # First upload a document
        text_content = "This is a test document with multiple sentences. It contains information about various topics."
        file_content = io.BytesIO(text_content.encode())
        
        upload_response = client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files={"file": ("test.txt", file_content, "text/plain")}
        )
        
        if upload_response.status_code == 200:
            # Ask a question with custom top_k
            response = client.post(
                "/api/v1/qa/ask",
                headers=auth_headers,
                json={
                    "question": "What information is available?",
                    "top_k": 1
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "answer" in data
            assert "sources" in data

    def test_ask_question_no_auth(self, client: TestClient):
        """Test asking a question without authentication"""
        response = client.post(
            "/api/v1/qa/ask",
            json={
                "question": "What is the capital of France?",
                "top_k": 5
            }
        )
        
        assert response.status_code == 401

    def test_ask_question_invalid_request(self, client: TestClient, auth_headers):
        """Test asking a question with invalid request data"""
        response = client.post(
            "/api/v1/qa/ask",
            headers=auth_headers,
            json={
                "question": "",  # Empty question
                "top_k": 5
            }
        )
        
        # This might pass validation but should handle empty questions gracefully
        assert response.status_code in [200, 422]

    def test_ask_question_large_top_k(self, client: TestClient, auth_headers, db_session: AsyncSession):
        """Test asking a question with a large top_k value"""
        # First upload a document
        text_content = "This is a test document."
        file_content = io.BytesIO(text_content.encode())
        
        upload_response = client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files={"file": ("test.txt", file_content, "text/plain")}
        )
        
        if upload_response.status_code == 200:
            # Ask a question with large top_k
            response = client.post(
                "/api/v1/qa/ask",
                headers=auth_headers,
                json={
                    "question": "What is this document about?",
                    "top_k": 100  # Large value
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "answer" in data
            assert "sources" in data

    def test_get_qa_stats(self, client: TestClient, auth_headers):
        """Test getting Q&A system statistics"""
        response = client.get("/api/v1/qa/stats", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "total_documents" in data
        assert "active_documents" in data
        assert "total_chunks" in data
        assert "faiss_index" in data

    def test_get_qa_stats_no_auth(self, client: TestClient):
        """Test getting Q&A stats without authentication"""
        response = client.get("/api/v1/qa/stats")
        
        assert response.status_code == 401

    def test_qa_with_multiple_documents(self, client: TestClient, auth_headers, db_session: AsyncSession):
        """Test Q&A with multiple documents"""
        # Upload first document
        text_content_1 = "Paris is the capital of France."
        file_content_1 = io.BytesIO(text_content_1.encode())
        
        upload_response_1 = client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files={"file": ("doc1.txt", file_content_1, "text/plain")}
        )
        
        # Upload second document
        text_content_2 = "London is the capital of England."
        file_content_2 = io.BytesIO(text_content_2.encode())
        
        upload_response_2 = client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files={"file": ("doc2.txt", file_content_2, "text/plain")}
        )
        
        if upload_response_1.status_code == 200 and upload_response_2.status_code == 200:
            # Ask a question that could match either document
            response = client.post(
                "/api/v1/qa/ask",
                headers=auth_headers,
                json={
                    "question": "What are the capitals mentioned?",
                    "top_k": 5
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "answer" in data
            assert "sources" in data

    def test_qa_complex_question(self, client: TestClient, auth_headers, db_session: AsyncSession):
        """Test Q&A with a complex question"""
        # Upload a document with complex content
        text_content = """
        Machine learning is a subset of artificial intelligence that focuses on algorithms 
        that can learn and make predictions from data. Deep learning is a subset of machine 
        learning that uses neural networks with multiple layers. Natural language processing 
        is a field that combines linguistics and computer science to enable computers to 
        understand and process human language.
        """
        file_content = io.BytesIO(text_content.encode())
        
        upload_response = client.post(
            "/api/v1/documents/upload",
            headers=auth_headers,
            files={"file": ("ml_doc.txt", file_content, "text/plain")}
        )
        
        if upload_response.status_code == 200:
            # Ask a complex question
            response = client.post(
                "/api/v1/qa/ask",
                headers=auth_headers,
                json={
                    "question": "What is the relationship between machine learning, deep learning, and natural language processing?",
                    "top_k": 3
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "answer" in data
            assert "sources" in data 