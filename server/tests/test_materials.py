"""
Tests for materials routes.
"""
import pytest
from fastapi import status
from io import BytesIO
from unittest.mock import patch, MagicMock


class TestUploadMaterial:
    """Tests for material upload endpoint."""
    
    def test_upload_text_file_success(self, authenticated_client, db_session):
        """Test successful text file upload."""
        text_content = "This is a test study material with enough content to be processed properly."
        
        with patch('app.routers.materials.auto_process_with_llm') as mock_llm:
            mock_llm.return_value = None
            
            response = authenticated_client.post(
                "/materials/upload-material",
                files={"file": ("test.txt", BytesIO(text_content.encode()), "text/plain")},
                params={"title": "Test Material"}
            )
        
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert result["title"] == "Test Material"
        assert result["content"] == text_content
        assert result["file_type"] == "text"
        assert "id" in result
        assert "uploaded_at" in result
    
    @patch('app.routers.materials.supabase_storage')
    def test_upload_pdf_file_success(self, mock_storage, authenticated_client):
        """Test successful PDF file upload."""
        # Create a minimal valid PDF
        pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 44 >>\nstream\nBT /F1 12 Tf 100 700 Td (Test PDF) Tj ET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000317 00000 n\ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n408\n%%EOF"
        
        mock_storage.supabase = MagicMock()
        mock_storage.upload_file.return_value = "https://example.com/test.pdf"
        
        with patch('app.routers.materials.auto_process_with_llm') as mock_llm:
            mock_llm.return_value = None
            
            response = authenticated_client.post(
                "/materials/upload-material",
                files={"file": ("test.pdf", BytesIO(pdf_content), "application/pdf")},
                params={"title": "Test PDF Material"}
            )
        
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert result["title"] == "Test PDF Material"
        assert result["file_type"] == "pdf"
        assert result["file_url"] == "https://example.com/test.pdf"
    
    def test_upload_unsupported_file_type(self, authenticated_client):
        """Test upload fails with unsupported file type."""
        response = authenticated_client.post(
            "/materials/upload-material",
            files={"file": ("test.jpg", BytesIO(b"fake image content"), "image/jpeg")},
            params={"title": "Test Image"}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "unsupported file type" in response.json()["detail"].lower()
    
    def test_upload_without_authentication(self, client):
        """Test upload fails without authentication."""
        response = client.post(
            "/materials/upload-material",
            files={"file": ("test.txt", BytesIO(b"test content"), "text/plain")},
            params={"title": "Test Material"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @patch('app.routers.materials.supabase_storage')
    def test_upload_pdf_storage_not_configured(self, mock_storage, authenticated_client):
        """Test PDF upload fails when storage is not configured."""
        mock_storage.supabase = None
        
        # Create a minimal valid PDF
        pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 44 >>\nstream\nBT /F1 12 Tf 100 700 Td (Test PDF) Tj ET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000317 00000 n\ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n408\n%%EOF"
        
        response = authenticated_client.post(
            "/materials/upload-material",
            files={"file": ("test.pdf", BytesIO(pdf_content), "application/pdf")},
            params={"title": "Test PDF"}
        )
        
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert "storage service" in response.json()["detail"].lower()


class TestUploadText:
    """Tests for direct text upload endpoint."""
    
    def test_upload_text_success(self, authenticated_client):
        """Test successful direct text upload."""
        text_data = {
            "title": "Direct Text Upload",
            "content": "This is a test content with enough characters to pass validation and be processed properly."
        }
        
        with patch('app.routers.materials.auto_process_with_llm') as mock_llm:
            mock_llm.return_value = None
            
            response = authenticated_client.post(
                "/materials/upload-text",
                json=text_data
            )
        
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert result["title"] == text_data["title"]
        assert result["content"] == text_data["content"]
        assert result["file_type"] == "text"
        assert result["file_url"] is None
    
    def test_upload_text_empty_title(self, authenticated_client):
        """Test upload fails with empty title."""
        text_data = {
            "title": "   ",
            "content": "This is valid content with enough characters to pass validation."
        }
        
        response = authenticated_client.post(
            "/materials/upload-text",
            json=text_data
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "title is required" in response.json()["detail"].lower()
    
    def test_upload_text_empty_content(self, authenticated_client):
        """Test upload fails with empty content."""
        text_data = {
            "title": "Valid Title",
            "content": "   "
        }
        
        response = authenticated_client.post(
            "/materials/upload-text",
            json=text_data
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "content is required" in response.json()["detail"].lower()
    
    def test_upload_text_too_short(self, authenticated_client):
        """Test upload fails with content too short."""
        text_data = {
            "title": "Valid Title",
            "content": "Too short"
        }
        
        response = authenticated_client.post(
            "/materials/upload-text",
            json=text_data
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "at least 50 characters" in response.json()["detail"].lower()
    
    def test_upload_text_without_authentication(self, client):
        """Test text upload fails without authentication."""
        text_data = {
            "title": "Test Title",
            "content": "This is test content with enough characters to pass validation."
        }
        
        response = client.post(
            "/materials/upload-text",
            json=text_data
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetUserHistory:
    """Tests for getting user's material history."""
    
    def test_get_history_empty(self, authenticated_client):
        """Test getting history when user has no materials."""
        response = authenticated_client.get("/materials/get-history")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
    
    def test_get_history_with_materials(self, authenticated_client, db_session):
        """Test getting history with uploaded materials."""
        # Upload two materials
        text_data_1 = {
            "title": "First Material",
            "content": "This is the first test material with enough content to be valid."
        }
        text_data_2 = {
            "title": "Second Material",
            "content": "This is the second test material with enough content to be valid."
        }
        
        with patch('app.routers.materials.auto_process_with_llm') as mock_llm:
            mock_llm.return_value = None
            authenticated_client.post("/materials/upload-text", json=text_data_1)
            authenticated_client.post("/materials/upload-text", json=text_data_2)
        
        response = authenticated_client.get("/materials/get-history")
        
        assert response.status_code == status.HTTP_200_OK
        history = response.json()
        assert len(history) == 2
        # Materials exist (order may vary based on timing)
        titles = [h["material"]["title"] for h in history]
        assert "First Material" in titles
        assert "Second Material" in titles
    
    def test_get_history_without_authentication(self, client):
        """Test getting history fails without authentication."""
        response = client.get("/materials/get-history")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_history_only_shows_user_materials(self, client, test_user_data, test_user_data_2, db_session):
        """Test users only see their own materials."""
        # Register and login first user
        client.post("/auth/register", json=test_user_data)
        client.post("/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        
        # Upload material as first user
        with patch('app.routers.materials.auto_process_with_llm') as mock_llm:
            mock_llm.return_value = None
            client.post("/materials/upload-text", json={
                "title": "User 1 Material",
                "content": "This is user 1's material with enough content to be valid."
            })
        
        # Logout and register second user
        client.post("/auth/logout")
        client.post("/auth/register", json=test_user_data_2)
        client.post("/auth/login", json={
            "email": test_user_data_2["email"],
            "password": test_user_data_2["password"]
        })
        
        # Upload material as second user
        with patch('app.routers.materials.auto_process_with_llm') as mock_llm:
            mock_llm.return_value = None
            client.post("/materials/upload-text", json={
                "title": "User 2 Material",
                "content": "This is user 2's material with enough content to be valid."
            })
        
        # Get history for second user
        response = client.get("/materials/get-history")
        
        assert response.status_code == status.HTTP_200_OK
        history = response.json()
        assert len(history) == 1
        assert history[0]["material"]["title"] == "User 2 Material"


class TestGetMaterial:
    """Tests for getting specific material by ID."""
    
    def test_get_material_success(self, authenticated_client):
        """Test successfully getting a specific material."""
        # Upload a material first
        text_data = {
            "title": "Test Material",
            "content": "This is test content with enough characters to pass validation."
        }
        
        with patch('app.routers.materials.auto_process_with_llm') as mock_llm:
            mock_llm.return_value = None
            upload_response = authenticated_client.post("/materials/upload-text", json=text_data)
        
        material_id = upload_response.json()["id"]
        
        # Get the material
        response = authenticated_client.get(f"/materials/{material_id}")
        
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert result["material"]["id"] == material_id
        assert result["material"]["title"] == text_data["title"]
    
    def test_get_material_not_found(self, authenticated_client):
        """Test getting non-existent material."""
        response = authenticated_client.get("/materials/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_material_wrong_user(self, client, test_user_data, test_user_data_2):
        """Test user cannot access another user's material."""
        # Register and login first user
        client.post("/auth/register", json=test_user_data)
        client.post("/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        
        # Upload material as first user
        with patch('app.routers.materials.auto_process_with_llm') as mock_llm:
            mock_llm.return_value = None
            upload_response = client.post("/materials/upload-text", json={
                "title": "User 1 Material",
                "content": "This is user 1's material with enough content to be valid."
            })
        
        material_id = upload_response.json()["id"]
        
        # Logout and login as second user
        client.post("/auth/logout")
        client.post("/auth/register", json=test_user_data_2)
        client.post("/auth/login", json={
            "email": test_user_data_2["email"],
            "password": test_user_data_2["password"]
        })
        
        # Try to access first user's material
        response = client.get(f"/materials/{material_id}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_material_without_authentication(self, client):
        """Test getting material fails without authentication."""
        response = client.get("/materials/1")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestDeleteMaterial:
    """Tests for deleting materials."""
    
    @patch('app.routers.materials.supabase_storage')
    def test_delete_material_success(self, mock_storage, authenticated_client):
        """Test successfully deleting a material."""
        mock_storage.supabase = MagicMock()
        mock_storage.delete_file.return_value = True
        
        # Upload a material first
        text_data = {
            "title": "Material to Delete",
            "content": "This material will be deleted with enough content to be valid."
        }
        
        with patch('app.routers.materials.auto_process_with_llm') as mock_llm:
            mock_llm.return_value = None
            upload_response = authenticated_client.post("/materials/upload-text", json=text_data)
        
        material_id = upload_response.json()["id"]
        
        # Delete the material
        response = authenticated_client.delete(f"/materials/{material_id}")
        
        assert response.status_code == status.HTTP_200_OK
        assert "deleted successfully" in response.json()["message"].lower()
        
        # Verify material is deleted
        get_response = authenticated_client.get(f"/materials/{material_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_material_not_found(self, authenticated_client):
        """Test deleting non-existent material."""
        response = authenticated_client.delete("/materials/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_material_wrong_user(self, client, test_user_data, test_user_data_2):
        """Test user cannot delete another user's material."""
        # Register and login first user
        client.post("/auth/register", json=test_user_data)
        client.post("/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        
        # Upload material as first user
        with patch('app.routers.materials.auto_process_with_llm') as mock_llm:
            mock_llm.return_value = None
            upload_response = client.post("/materials/upload-text", json={
                "title": "User 1 Material",
                "content": "This is user 1's material with enough content to be valid."
            })
        
        material_id = upload_response.json()["id"]
        
        # Logout and login as second user
        client.post("/auth/logout")
        client.post("/auth/register", json=test_user_data_2)
        client.post("/auth/login", json={
            "email": test_user_data_2["email"],
            "password": test_user_data_2["password"]
        })
        
        # Try to delete first user's material
        response = client.delete(f"/materials/{material_id}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_material_without_authentication(self, client):
        """Test deleting material fails without authentication."""
        response = client.delete("/materials/1")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetDownloadUrl:
    """Tests for getting download URL."""
    
    @patch('app.routers.materials.supabase_storage')
    def test_get_download_url_success(self, mock_storage, authenticated_client):
        """Test successfully getting download URL."""
        mock_storage.supabase = MagicMock()
        mock_storage.upload_file.return_value = "https://example.com/test.pdf"
        mock_storage.generate_presigned_url.return_value = "https://example.com/test.pdf?signed=true"
        
        # Upload a PDF material with valid PDF content
        pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 44 >>\nstream\nBT /F1 12 Tf 100 700 Td (Test PDF) Tj ET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000317 00000 n\ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n408\n%%EOF"
        
        with patch('app.routers.materials.auto_process_with_llm') as mock_llm:
            mock_llm.return_value = None
            upload_response = authenticated_client.post(
                "/materials/upload-material",
                files={"file": ("test.pdf", BytesIO(pdf_content), "application/pdf")},
                params={"title": "Test PDF"}
            )
        
        material_id = upload_response.json()["id"]
        
        # Get download URL
        response = authenticated_client.get(f"/materials/download/{material_id}")
        
        assert response.status_code == status.HTTP_200_OK
        assert "download_url" in response.json()
        assert response.json()["download_url"] == "https://example.com/test.pdf?signed=true"
    
    def test_get_download_url_no_file(self, authenticated_client):
        """Test getting download URL for material without file."""
        # Upload text material (no file)
        text_data = {
            "title": "Text Material",
            "content": "This is text content with enough characters to be valid."
        }
        
        with patch('app.routers.materials.auto_process_with_llm') as mock_llm:
            mock_llm.return_value = None
            upload_response = authenticated_client.post("/materials/upload-text", json=text_data)
        
        material_id = upload_response.json()["id"]
        
        # Try to get download URL
        response = authenticated_client.get(f"/materials/download/{material_id}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "no file" in response.json()["detail"].lower()
    
    def test_get_download_url_not_found(self, authenticated_client):
        """Test getting download URL for non-existent material."""
        response = authenticated_client.get("/materials/download/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_download_url_without_authentication(self, client):
        """Test getting download URL fails without authentication."""
        response = client.get("/materials/download/1")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
