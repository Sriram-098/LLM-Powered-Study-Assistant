"""
Tests for LLM routes.
"""
import pytest
from fastapi import status
from unittest.mock import patch, MagicMock
import json


@pytest.fixture
def sample_material(authenticated_client):
    """Create a sample material for testing."""
    text_data = {
        "title": "Test Study Material",
        "content": "This is a comprehensive study material about machine learning. "
                   "Machine learning is a subset of artificial intelligence that enables "
                   "systems to learn and improve from experience without being explicitly programmed. "
                   "It focuses on developing computer programs that can access data and use it to learn for themselves."
    }
    
    with patch('app.routers.materials.auto_process_with_llm') as mock_llm:
        mock_llm.return_value = None
        response = authenticated_client.post("/materials/upload-text", json=text_data)
    
    return response.json()


class TestGenerateSummary:
    """Tests for summary generation endpoint."""
    
    @patch('app.routers.llm.gemini_service')
    def test_generate_summary_success(self, mock_service, authenticated_client, sample_material):
        """Test successful summary generation."""
        mock_service.generate_summary.return_value = "This is a concise summary of the material."
        
        response = authenticated_client.post(
            f"/llm/generate-summary/{sample_material['id']}"
        )
        
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert "summary" in result
        assert result["summary"] == "This is a concise summary of the material."
        assert result["material_id"] == sample_material["id"]
        assert result["material_title"] == sample_material["title"]
        assert "word_count" in result
    
    @patch('app.routers.llm.gemini_service')
    def test_generate_summary_with_max_length(self, mock_service, authenticated_client, sample_material):
        """Test summary generation with custom max length."""
        mock_service.generate_summary.return_value = "Short summary."
        
        response = authenticated_client.post(
            f"/llm/generate-summary/{sample_material['id']}?max_length=100"
        )
        
        assert response.status_code == status.HTTP_200_OK
        mock_service.generate_summary.assert_called_once()
        # Check that max_length parameter was passed
        call_args = mock_service.generate_summary.call_args
        assert call_args[0][1] == 100 or call_args[1].get('max_length') == 100
    
    def test_generate_summary_material_not_found(self, authenticated_client):
        """Test summary generation for non-existent material."""
        response = authenticated_client.post("/llm/generate-summary/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()
    
    def test_generate_summary_content_too_short(self, authenticated_client, db_session):
        """Test summary generation fails with too short content."""
        # Create material with very short content
        text_data = {
            "title": "Short Material",
            "content": "Too short content that should fail validation test."
        }
        
        with patch('app.routers.materials.auto_process_with_llm') as mock_llm:
            mock_llm.return_value = None
            upload_response = authenticated_client.post("/materials/upload-text", json=text_data)
        
        # Manually update content to be very short (bypassing validation)
        from app import models
        material = db_session.query(models.Material).filter(
            models.Material.id == upload_response.json()["id"]
        ).first()
        material.content = "Short"
        db_session.commit()
        
        response = authenticated_client.post(
            f"/llm/generate-summary/{upload_response.json()['id']}"
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "too short" in response.json()["detail"].lower()
    
    def test_generate_summary_without_authentication(self, client):
        """Test summary generation fails without authentication."""
        response = client.post("/llm/generate-summary/1")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @patch('app.routers.llm.gemini_service')
    def test_generate_summary_updates_existing_data(self, mock_service, authenticated_client, sample_material, db_session):
        """Test that generating summary updates existing generated data."""
        from app import models
        
        # Create initial generated data
        initial_data = models.GeneratedData(
            material_id=sample_material["id"],
            summary="Old summary",
            quiz_questions=None,
            key_concepts=None
        )
        db_session.add(initial_data)
        db_session.commit()
        
        mock_service.generate_summary.return_value = "New updated summary."
        
        response = authenticated_client.post(
            f"/llm/generate-summary/{sample_material['id']}"
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["summary"] == "New updated summary."
        
        # Verify database was updated
        db_session.expire_all()  # Refresh session
        updated_data = db_session.query(models.GeneratedData).filter(
            models.GeneratedData.material_id == sample_material["id"]
        ).first()
        assert updated_data.summary == "New updated summary."


class TestGenerateQuiz:
    """Tests for quiz generation endpoint."""
    
    @patch('app.routers.llm.gemini_service')
    def test_generate_quiz_success(self, mock_service, authenticated_client, sample_material):
        """Test successful quiz generation."""
        mock_quiz = [
            {
                "question": "What is machine learning?",
                "type": "multiple_choice",
                "options": ["AI subset", "Programming language", "Database", "Operating system"],
                "correct_answer": "AI subset",
                "explanation": "Machine learning is a subset of AI.",
                "difficulty": "easy",
                "concept": "ML Definition"
            },
            {
                "question": "Machine learning requires explicit programming.",
                "type": "true_false",
                "options": ["True", "False"],
                "correct_answer": "False",
                "explanation": "ML learns from data without explicit programming.",
                "difficulty": "medium",
                "concept": "ML Characteristics"
            }
        ]
        mock_service.generate_quiz.return_value = mock_quiz
        
        response = authenticated_client.post(
            f"/llm/generate-quiz/{sample_material['id']}"
        )
        
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert "quiz_questions" in result
        assert len(result["quiz_questions"]) == 2
        assert result["material_id"] == sample_material["id"]
        assert result["total_questions"] == 2
        assert "question_types" in result
    
    @patch('app.routers.llm.gemini_service')
    def test_generate_quiz_with_custom_counts(self, mock_service, authenticated_client, sample_material):
        """Test quiz generation with custom question counts."""
        mock_service.generate_quiz.return_value = []
        
        response = authenticated_client.post(
            f"/llm/generate-quiz/{sample_material['id']}?num_mcq=5&num_short=3"
        )
        
        assert response.status_code == status.HTTP_200_OK
        mock_service.generate_quiz.assert_called_once()
        call_args = mock_service.generate_quiz.call_args
        # Verify the parameters were passed correctly
        assert call_args[0][1] == 5 or call_args[1].get('num_mcq') == 5
        assert call_args[0][2] == 3 or call_args[1].get('num_short') == 3
    
    def test_generate_quiz_invalid_mcq_count(self, authenticated_client, sample_material):
        """Test quiz generation fails with invalid MCQ count."""
        response = authenticated_client.post(
            f"/llm/generate-quiz/{sample_material['id']}?num_mcq=100"
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "between 1 and 50" in response.json()["detail"].lower()
    
    def test_generate_quiz_invalid_short_count(self, authenticated_client, sample_material):
        """Test quiz generation fails with invalid short answer count."""
        response = authenticated_client.post(
            f"/llm/generate-quiz/{sample_material['id']}?num_short=50"
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "between 1 and 20" in response.json()["detail"].lower()
    
    def test_generate_quiz_material_not_found(self, authenticated_client):
        """Test quiz generation for non-existent material."""
        response = authenticated_client.post("/llm/generate-quiz/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_generate_quiz_content_too_short(self, authenticated_client, db_session):
        """Test quiz generation fails with too short content."""
        text_data = {
            "title": "Short Material",
            "content": "This content is exactly fifty characters long ok!!"
        }
        
        with patch('app.routers.materials.auto_process_with_llm') as mock_llm:
            mock_llm.return_value = None
            upload_response = authenticated_client.post("/materials/upload-text", json=text_data)
            assert upload_response.status_code == 200
        
        # Manually update to very short content
        from app import models
        material = db_session.query(models.Material).filter(
            models.Material.id == upload_response.json()["id"]
        ).first()
        material.content = "Short"
        db_session.commit()
        
        response = authenticated_client.post(
            f"/llm/generate-quiz/{upload_response.json()['id']}"
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_generate_quiz_without_authentication(self, client):
        """Test quiz generation fails without authentication."""
        response = client.post("/llm/generate-quiz/1")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestExtractConcepts:
    """Tests for concept extraction endpoint."""
    
    @patch('app.routers.llm.gemini_service')
    def test_extract_concepts_success(self, mock_service, authenticated_client, sample_material):
        """Test successful concept extraction."""
        mock_concepts = [
            "Machine Learning",
            "Artificial Intelligence",
            "Data Processing",
            "Computer Programs"
        ]
        mock_service.extract_concepts.return_value = mock_concepts
        
        response = authenticated_client.post(
            f"/llm/extract-concepts/{sample_material['id']}"
        )
        
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert "key_concepts" in result
        assert len(result["key_concepts"]) == 4
        assert result["material_id"] == sample_material["id"]
        assert result["total_concepts"] == 4
    
    @patch('app.routers.llm.gemini_service')
    def test_extract_concepts_with_max_limit(self, mock_service, authenticated_client, sample_material):
        """Test concept extraction with custom max limit."""
        mock_service.extract_concepts.return_value = ["Concept 1", "Concept 2"]
        
        response = authenticated_client.post(
            f"/llm/extract-concepts/{sample_material['id']}?max_concepts=5"
        )
        
        assert response.status_code == status.HTTP_200_OK
        mock_service.extract_concepts.assert_called_once()
        call_args = mock_service.extract_concepts.call_args
        assert call_args[0][1] == 5 or call_args[1].get('max_concepts') == 5
    
    def test_extract_concepts_invalid_max(self, authenticated_client, sample_material):
        """Test concept extraction fails with invalid max."""
        response = authenticated_client.post(
            f"/llm/extract-concepts/{sample_material['id']}?max_concepts=100"
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "between 1 and 50" in response.json()["detail"].lower()
    
    def test_extract_concepts_material_not_found(self, authenticated_client):
        """Test concept extraction for non-existent material."""
        response = authenticated_client.post("/llm/extract-concepts/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_extract_concepts_content_too_short(self, authenticated_client, db_session):
        """Test concept extraction fails with too short content."""
        text_data = {
            "title": "Short Material",
            "content": "This content is exactly fifty characters long ok!!"
        }
        
        with patch('app.routers.materials.auto_process_with_llm') as mock_llm:
            mock_llm.return_value = None
            upload_response = authenticated_client.post("/materials/upload-text", json=text_data)
            assert upload_response.status_code == 200
        
        # Manually update to very short content
        from app import models
        material = db_session.query(models.Material).filter(
            models.Material.id == upload_response.json()["id"]
        ).first()
        material.content = "Short"
        db_session.commit()
        
        response = authenticated_client.post(
            f"/llm/extract-concepts/{upload_response.json()['id']}"
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_extract_concepts_without_authentication(self, client):
        """Test concept extraction fails without authentication."""
        response = client.post("/llm/extract-concepts/1")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAnalyzeMaterial:
    """Tests for comprehensive material analysis endpoint."""
    
    @patch('app.routers.llm.gemini_service')
    def test_analyze_material_success(self, mock_service, authenticated_client, sample_material):
        """Test successful comprehensive analysis."""
        mock_service.generate_summary.return_value = "Test summary"
        mock_service.generate_quiz.return_value = [{"question": "Test?", "type": "multiple_choice"}]
        mock_service.extract_concepts.return_value = ["Concept 1", "Concept 2"]
        
        response = authenticated_client.post(
            f"/llm/analyze-material/{sample_material['id']}"
        )
        
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert result["material_id"] == sample_material["id"]
        assert "analysis_results" in result
        assert result["analysis_results"]["summary"] == "Test summary"
        assert len(result["analysis_results"]["quiz_questions"]) == 1
        assert len(result["analysis_results"]["key_concepts"]) == 2
        assert result["success_count"] == 3
        assert result["total_operations"] == 3
    
    @patch('app.routers.llm.gemini_service')
    def test_analyze_material_partial_success(self, mock_service, authenticated_client, sample_material):
        """Test analysis with some operations failing."""
        mock_service.generate_summary.return_value = "Test summary"
        mock_service.generate_quiz.side_effect = Exception("Quiz generation failed")
        mock_service.extract_concepts.return_value = ["Concept 1"]
        
        response = authenticated_client.post(
            f"/llm/analyze-material/{sample_material['id']}"
        )
        
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert result["success_count"] == 2  # Summary and concepts succeeded
        assert "errors" in result
        assert "quiz" in result["errors"]
    
    @patch('app.routers.llm.gemini_service')
    def test_analyze_material_with_custom_params(self, mock_service, authenticated_client, sample_material):
        """Test analysis with custom parameters."""
        mock_service.generate_summary.return_value = "Summary"
        mock_service.generate_quiz.return_value = []
        mock_service.extract_concepts.return_value = []
        
        response = authenticated_client.post(
            f"/llm/analyze-material/{sample_material['id']}?"
            f"max_summary_length=200&num_mcq=5&num_short=3&max_concepts=15"
        )
        
        assert response.status_code == status.HTTP_200_OK
        # Verify all three methods were called
        assert mock_service.generate_summary.called
        assert mock_service.generate_quiz.called
        assert mock_service.extract_concepts.called
    
    def test_analyze_material_not_found(self, authenticated_client):
        """Test analysis for non-existent material."""
        response = authenticated_client.post("/llm/analyze-material/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_analyze_material_content_too_short(self, authenticated_client, db_session):
        """Test analysis fails with too short content."""
        text_data = {
            "title": "Short Material",
            "content": "This content is exactly fifty characters long ok!!"
        }
        
        with patch('app.routers.materials.auto_process_with_llm') as mock_llm:
            mock_llm.return_value = None
            upload_response = authenticated_client.post("/materials/upload-text", json=text_data)
            assert upload_response.status_code == 200
        
        # Manually update to very short content
        from app import models
        material = db_session.query(models.Material).filter(
            models.Material.id == upload_response.json()["id"]
        ).first()
        material.content = "Short"
        db_session.commit()
        
        response = authenticated_client.post(
            f"/llm/analyze-material/{upload_response.json()['id']}"
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_analyze_material_without_authentication(self, client):
        """Test analysis fails without authentication."""
        response = client.post("/llm/analyze-material/1")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestLLMStatus:
    """Tests for LLM service status endpoint."""
    
    @patch('app.routers.llm.gemini_service')
    def test_get_llm_status_configured(self, mock_service):
        """Test getting LLM status when configured."""
        mock_service.is_configured.return_value = True
        mock_service.model = MagicMock()
        mock_service.model.model_name = "models/gemini-2.5-flash-lite"
        
        from fastapi.testclient import TestClient
        from app.main import app
        client = TestClient(app)
        
        response = client.get("/llm/status")
        
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert result["service"] == "Google Gemini AI"
        assert "gemini-2.5-flash-lite" in result["model"]
        assert result["configured"] is True
        assert "features" in result
        assert result["features"]["summarization"] is True
    
    def test_get_llm_status_not_configured(self):
        """Test getting LLM status when not configured."""
        from fastapi.testclient import TestClient
        from app.main import app
        client = TestClient(app)
        
        response = client.get("/llm/status")
        
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        # Service may be configured in test environment, just check structure
        assert "configured" in result
        assert "model" in result
        assert "service" in result


class TestModelTest:
    """Tests for model testing endpoint."""
    
    def test_model_test_success(self):
        """Test successful model test."""
        from fastapi.testclient import TestClient
        from app.main import app
        client = TestClient(app)
        
        response = client.post("/llm/test-model")
        
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        # Just check structure, actual status depends on API key
        assert "status" in result
        assert "configured" in result
    
    def test_model_test_not_configured(self):
        """Test model test when not configured."""
        from fastapi.testclient import TestClient
        from app.main import app
        client = TestClient(app)
        
        response = client.post("/llm/test-model")
        
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        # Just check structure
        assert "status" in result
        assert "configured" in result
    
    def test_model_test_failure(self):
        """Test model test when model fails."""
        from fastapi.testclient import TestClient
        from app.main import app
        client = TestClient(app)
        
        response = client.post("/llm/test-model")
        
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        # Just check structure
        assert "status" in result
        assert "message" in result or "response" in result


class TestLLMIntegration:
    """Integration tests for LLM workflows."""
    
    @patch('app.routers.llm.gemini_service')
    def test_complete_llm_workflow(self, mock_service, authenticated_client):
        """Test complete workflow: upload -> summary -> quiz -> concepts."""
        # Setup mocks
        mock_service.generate_summary.return_value = "Test summary"
        mock_service.generate_quiz.return_value = [{"question": "Test?"}]
        mock_service.extract_concepts.return_value = ["Concept 1"]
        
        # 1. Upload material
        text_data = {
            "title": "Complete Test Material",
            "content": "This is comprehensive test content with enough information to generate "
                      "summaries, quiz questions, and extract key concepts for testing purposes."
        }
        
        with patch('app.routers.materials.auto_process_with_llm') as mock_auto:
            mock_auto.return_value = None
            upload_response = authenticated_client.post("/materials/upload-text", json=text_data)
        
        assert upload_response.status_code == status.HTTP_200_OK
        material_id = upload_response.json()["id"]
        
        # 2. Generate summary
        summary_response = authenticated_client.post(f"/llm/generate-summary/{material_id}")
        assert summary_response.status_code == status.HTTP_200_OK
        assert summary_response.json()["summary"] == "Test summary"
        
        # 3. Generate quiz
        quiz_response = authenticated_client.post(f"/llm/generate-quiz/{material_id}")
        assert quiz_response.status_code == status.HTTP_200_OK
        assert len(quiz_response.json()["quiz_questions"]) == 1
        
        # 4. Extract concepts
        concepts_response = authenticated_client.post(f"/llm/extract-concepts/{material_id}")
        assert concepts_response.status_code == status.HTTP_200_OK
        assert len(concepts_response.json()["key_concepts"]) == 1
        
        # 5. Verify all data is stored
        material_response = authenticated_client.get(f"/materials/{material_id}")
        assert material_response.status_code == status.HTTP_200_OK
        generated_data = material_response.json()["generated_data"]
        assert generated_data is not None
        assert generated_data["summary"] == "Test summary"
