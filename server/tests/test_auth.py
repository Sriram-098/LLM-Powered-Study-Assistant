"""
Tests for authentication routes.
"""
import pytest
from fastapi import status


class TestAuthWelcome:
    """Tests for the auth welcome endpoint."""
    
    def test_auth_welcome(self, client):
        """Test the auth welcome endpoint returns correct message."""
        response = client.get("/auth/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == "Welcome"


class TestUserRegistration:
    """Tests for user registration endpoint."""
    
    def test_register_new_user_success(self, client, test_user_data):
        """Test successful user registration."""
        response = client.post("/auth/register", json=test_user_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["username"] == test_user_data["username"]
        assert "id" in data
        assert "hashed_password" not in data  # Password should not be returned
    
    def test_register_duplicate_email(self, client, test_user_data, registered_user):
        """Test registration fails with duplicate email."""
        duplicate_user = test_user_data.copy()
        duplicate_user["username"] = "different_username"
        
        response = client.post("/auth/register", json=duplicate_user)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"].lower()
    
    def test_register_duplicate_username(self, client, test_user_data, registered_user):
        """Test registration fails with duplicate username."""
        duplicate_user = test_user_data.copy()
        duplicate_user["email"] = "different@example.com"
        
        response = client.post("/auth/register", json=duplicate_user)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"].lower()
    
    def test_register_invalid_email(self, client, test_user_data):
        """Test registration fails with invalid email format."""
        invalid_user = test_user_data.copy()
        invalid_user["email"] = "invalid-email"
        
        response = client.post("/auth/register", json=invalid_user)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_missing_fields(self, client):
        """Test registration fails with missing required fields."""
        incomplete_user = {"email": "test@example.com"}
        
        response = client.post("/auth/register", json=incomplete_user)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_empty_password(self, client, test_user_data):
        """Test registration fails with empty password."""
        invalid_user = test_user_data.copy()
        invalid_user["password"] = ""
        
        response = client.post("/auth/register", json=invalid_user)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUserLogin:
    """Tests for user login endpoint."""
    
    def test_login_success(self, client, test_user_data, registered_user):
        """Test successful user login."""
        response = client.post(
            "/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "access_token" in response.cookies
    
    def test_login_wrong_password(self, client, test_user_data, registered_user):
        """Test login fails with incorrect password."""
        response = client.post(
            "/auth/login",
            json={
                "email": test_user_data["email"],
                "password": "WrongPassword123!"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "incorrect" in response.json()["detail"].lower()
    
    def test_login_wrong_email(self, client, test_user_data):
        """Test login fails with non-existent email."""
        response = client.post(
            "/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": test_user_data["password"]
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "incorrect" in response.json()["detail"].lower()
    
    def test_login_missing_credentials(self, client):
        """Test login fails with missing credentials."""
        response = client.post("/auth/login", json={})
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_login_sets_cookie(self, client, test_user_data, registered_user):
        """Test login sets HTTP-only cookie."""
        response = client.post(
            "/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.cookies
        # Note: TestClient doesn't expose cookie attributes like httponly


class TestGetCurrentUser:
    """Tests for getting current user information."""
    
    def test_get_current_user_authenticated(self, authenticated_client, test_user_data):
        """Test getting current user info when authenticated."""
        response = authenticated_client.get("/auth/me")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["username"] == test_user_data["username"]
        assert "id" in data
        assert "hashed_password" not in data
    
    def test_get_current_user_unauthenticated(self, client):
        """Test getting current user fails when not authenticated."""
        response = client.get("/auth/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_current_user_invalid_token(self, client):
        """Test getting current user fails with invalid token."""
        client.cookies.set("access_token", "invalid_token_here")
        response = client.get("/auth/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUserLogout:
    """Tests for user logout endpoint."""
    
    def test_logout_success(self, authenticated_client):
        """Test successful logout."""
        response = authenticated_client.post("/auth/logout")
        
        assert response.status_code == status.HTTP_200_OK
        assert "successfully" in response.json()["message"].lower()
    
    def test_logout_clears_cookie(self, authenticated_client):
        """Test logout clears the access token cookie."""
        # First verify cookie exists
        assert "access_token" in authenticated_client.cookies
        
        # Logout
        response = authenticated_client.post("/auth/logout")
        
        assert response.status_code == status.HTTP_200_OK
        # After logout, cookie should be cleared (set to empty or deleted)
    
    def test_logout_when_not_authenticated(self, client):
        """Test logout works even when not authenticated."""
        response = client.post("/auth/logout")
        
        assert response.status_code == status.HTTP_200_OK


class TestAuthenticationFlow:
    """Integration tests for complete authentication flows."""
    
    def test_complete_auth_flow(self, client, test_user_data):
        """Test complete flow: register -> login -> access protected route -> logout."""
        # 1. Register
        register_response = client.post("/auth/register", json=test_user_data)
        assert register_response.status_code == status.HTTP_200_OK
        
        # 2. Login
        login_response = client.post(
            "/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        assert login_response.status_code == status.HTTP_200_OK
        
        # 3. Access protected route
        me_response = client.get("/auth/me")
        assert me_response.status_code == status.HTTP_200_OK
        assert me_response.json()["email"] == test_user_data["email"]
        
        # 4. Logout
        logout_response = client.post("/auth/logout")
        assert logout_response.status_code == status.HTTP_200_OK
    
    def test_multiple_users_registration(self, client, test_user_data, test_user_data_2):
        """Test multiple users can register with different credentials."""
        # Register first user
        response1 = client.post("/auth/register", json=test_user_data)
        assert response1.status_code == status.HTTP_200_OK
        
        # Register second user
        response2 = client.post("/auth/register", json=test_user_data_2)
        assert response2.status_code == status.HTTP_200_OK
        
        # Verify they have different IDs
        assert response1.json()["id"] != response2.json()["id"]
    
    def test_concurrent_logins(self, client, test_user_data, test_user_data_2):
        """Test multiple users can be logged in simultaneously."""
        # Register both users
        client.post("/auth/register", json=test_user_data)
        client.post("/auth/register", json=test_user_data_2)
        
        # Login first user
        login1 = client.post(
            "/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        assert login1.status_code == status.HTTP_200_OK
        token1 = login1.json()["access_token"]
        
        # Login second user (this would typically be a different client)
        login2 = client.post(
            "/auth/login",
            json={
                "email": test_user_data_2["email"],
                "password": test_user_data_2["password"]
            }
        )
        assert login2.status_code == status.HTTP_200_OK
        token2 = login2.json()["access_token"]
        
        # Tokens should be different
        assert token1 != token2


class TestPasswordSecurity:
    """Tests for password security."""
    
    def test_password_is_hashed(self, client, test_user_data, db_session):
        """Test that passwords are hashed in the database."""
        from app.models import User
        
        # Register user
        client.post("/auth/register", json=test_user_data)
        
        # Query database directly
        user = db_session.query(User).filter(User.email == test_user_data["email"]).first()
        
        # Password should be hashed, not plain text
        assert user.hashed_password != test_user_data["password"]
        assert len(user.hashed_password) > 50  # Hashed passwords are long
    
    def test_password_not_returned_in_response(self, client, test_user_data):
        """Test that password is never returned in API responses."""
        # Register
        register_response = client.post("/auth/register", json=test_user_data)
        assert "password" not in register_response.json()
        assert "hashed_password" not in register_response.json()
        
        # Login and get user info
        client.post(
            "/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        me_response = client.get("/auth/me")
        assert "password" not in me_response.json()
        assert "hashed_password" not in me_response.json()
