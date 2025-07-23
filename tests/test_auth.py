import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import UserRole


class TestAuth:
    def test_signup_success(self, client: TestClient):
        """Test successful user signup"""
        response = client.post("/api/v1/auth/signup", json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "newpassword123",
            "role": "editor"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert data["role"] == "editor"
        assert "id" in data

    def test_signup_duplicate_username(self, client: TestClient, test_user):
        """Test signup with duplicate username"""
        response = client.post("/api/v1/auth/signup", json={
            "email": "different@example.com",
            "username": "testuser",  # Already exists
            "password": "password123",
            "role": "viewer"
        })
        
        assert response.status_code == 400
        assert "Username already registered" in response.json()["detail"]

    def test_signup_duplicate_email(self, client: TestClient, test_user):
        """Test signup with duplicate email"""
        response = client.post("/api/v1/auth/signup", json={
            "email": "test@example.com",  # Already exists
            "username": "differentuser",
            "password": "password123",
            "role": "viewer"
        })
        
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    def test_login_success(self, client: TestClient, test_user):
        """Test successful login"""
        response = client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": "testpassword"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client: TestClient, test_user):
        """Test login with invalid credentials"""
        response = client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with nonexistent user"""
        response = client.post("/api/v1/auth/login", json={
            "username": "nonexistent",
            "password": "password123"
        })
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_get_current_user(self, client: TestClient, auth_headers):
        """Test getting current user info"""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["role"] == "editor"

    def test_get_current_user_no_token(self, client: TestClient):
        """Test getting current user without token"""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == 401

    def test_update_current_user(self, client: TestClient, auth_headers):
        """Test updating current user"""
        response = client.put("/api/v1/auth/me", 
                            headers=auth_headers,
                            json={
                                "email": "updated@example.com",
                                "username": "updateduser"
                            })
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "updated@example.com"
        assert data["username"] == "updateduser"

    def test_update_user_admin(self, client: TestClient, admin_headers, test_user):
        """Test admin updating another user"""
        response = client.put(f"/api/v1/auth/users/{test_user.id}",
                            headers=admin_headers,
                            json={
                                "role": "viewer",
                                "is_active": False
                            })
        
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "viewer"
        assert data["is_active"] == False

    def test_update_user_not_admin(self, client: TestClient, auth_headers, test_user):
        """Test non-admin trying to update another user"""
        response = client.put(f"/api/v1/auth/users/{test_user.id}",
                            headers=auth_headers,
                            json={"role": "viewer"})
        
        assert response.status_code == 403 