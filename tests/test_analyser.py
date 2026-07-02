"""
test_analyser.py
----------------
Unit tests for the analyser module.
Tests use mock API responses to avoid real API calls during testing.

Run with:
    pytest tests/
"""

import pytest
import json
from unittest.mock import patch, MagicMock


# ── Mock data ──────────────────────────────────────────────────────────────────

MOCK_JOB_SKILLS = {
    "job_title": "Data Scientist",
    "company": "TechCorp",
    "required_skills": [
        {"skill": "Python", "category": "Programming", "importance": "must-have"},
        {"skill": "Machine Learning", "category": "Machine Learning", "importance": "must-have"},
        {"skill": "SQL", "category": "Programming", "importance": "must-have"},
        {"skill": "AWS", "category": "Cloud", "importance": "nice-to-have"},
    ],
    "experience_years": "2-4 years",
    "key_responsibilities": ["Build ML models", "Analyse data"]
}

MOCK_CANDIDATE_SKILLS = {
    "candidate_name": "Aishwarya Rathudi",
    "education": "MSc Data Analytics",
    "total_experience_years": 3,
    "skills": [
        {"skill": "Python", "category": "Programming", "proficiency": "Proficient", "evidence": "iNeuron internship"},
        {"skill": "SQL", "category": "Programming", "proficiency": "Proficient", "evidence": "WFM role"},
        {"skill": "Machine Learning", "category": "Machine Learning", "proficiency": "Proficient", "evidence": "Scikit-learn projects"},
    ]
}

MOCK_GAP_ANALYSIS = {
    "overall_match_score": 75,
    "match_summary": "Strong foundational fit with Python, SQL, and ML skills.",
    "matched_skills": [
        {"skill": "Python", "category": "Programming", "candidate_level": "Proficient"},
        {"skill": "SQL", "category": "Programming", "candidate_level": "Proficient"},
    ],
    "gap_skills": [
        {"skill": "AWS", "category": "Cloud", "importance": "nice-to-have",
         "learning_resource": "AWS Cloud Practitioner course", "estimated_time": "3 weeks"},
    ],
    "strengths": ["Strong Python skills", "ML experience"],
    "quick_wins": ["Get AWS certified", "Add a Streamlit project"],
    "interview_talking_points": ["MLOps experience with CI/CD", "20% model accuracy improvement"]
}


# ── Fixtures ───────────────────────────────────────────────────────────────────

def make_mock_message(content_dict: dict):
    """Helper: create a mock Anthropic API response."""
    mock_msg = MagicMock()
    mock_msg.content = [MagicMock(text=json.dumps(content_dict))]
    return mock_msg


# ── Tests ──────────────────────────────────────────────────────────────────────

class TestExtractJobSkills:
    
    @patch("src.analyser.client")
    def test_returns_dict_with_required_keys(self, mock_client):
        mock_client.messages.create.return_value = make_mock_message(MOCK_JOB_SKILLS)
        
        from src.analyser import extract_job_skills
        result = extract_job_skills("We are hiring a Data Scientist...")
        
        assert isinstance(result, dict)
        assert "job_title" in result
        assert "required_skills" in result
        assert isinstance(result["required_skills"], list)
    
    @patch("src.analyser.client")
    def test_skills_have_required_fields(self, mock_client):
        mock_client.messages.create.return_value = make_mock_message(MOCK_JOB_SKILLS)
        
        from src.analyser import extract_job_skills
        result = extract_job_skills("We are hiring a Data Scientist...")
        
        for skill in result["required_skills"]:
            assert "skill" in skill
            assert "category" in skill
            assert "importance" in skill


class TestExtractCVSkills:
    
    @patch("src.analyser.client")
    def test_returns_candidate_name(self, mock_client):
        mock_client.messages.create.return_value = make_mock_message(MOCK_CANDIDATE_SKILLS)
        
        from src.analyser import extract_cv_skills
        result = extract_cv_skills("Aishwarya Rathudi, Data Scientist...")
        
        assert result["candidate_name"] == "Aishwarya Rathudi"
    
    @patch("src.analyser.client")
    def test_skills_list_not_empty(self, mock_client):
        mock_client.messages.create.return_value = make_mock_message(MOCK_CANDIDATE_SKILLS)
        
        from src.analyser import extract_cv_skills
        result = extract_cv_skills("Some CV text...")
        
        assert len(result["skills"]) > 0


class TestGapAnalysis:
    
    @patch("src.analyser.client")
    def test_score_in_valid_range(self, mock_client):
        mock_client.messages.create.return_value = make_mock_message(MOCK_GAP_ANALYSIS)
        
        from src.analyser import run_gap_analysis
        result = run_gap_analysis(MOCK_JOB_SKILLS, MOCK_CANDIDATE_SKILLS)
        
        score = result["overall_match_score"]
        assert 0 <= score <= 100
    
    @patch("src.analyser.client")
    def test_has_matched_and_gap_skills(self, mock_client):
        mock_client.messages.create.return_value = make_mock_message(MOCK_GAP_ANALYSIS)
        
        from src.analyser import run_gap_analysis
        result = run_gap_analysis(MOCK_JOB_SKILLS, MOCK_CANDIDATE_SKILLS)
        
        assert "matched_skills" in result
        assert "gap_skills" in result
        assert isinstance(result["matched_skills"], list)
        assert isinstance(result["gap_skills"], list)
    
    @patch("src.analyser.client")
    def test_has_actionable_outputs(self, mock_client):
        mock_client.messages.create.return_value = make_mock_message(MOCK_GAP_ANALYSIS)
        
        from src.analyser import run_gap_analysis
        result = run_gap_analysis(MOCK_JOB_SKILLS, MOCK_CANDIDATE_SKILLS)
        
        assert len(result.get("quick_wins", [])) > 0
        assert len(result.get("interview_talking_points", [])) > 0


class TestFullAnalysis:
    
    @patch("src.analyser.client")
    def test_full_pipeline_returns_all_sections(self, mock_client):
        # Mock three successive API calls
        mock_client.messages.create.side_effect = [
            make_mock_message(MOCK_JOB_SKILLS),
            make_mock_message(MOCK_CANDIDATE_SKILLS),
            make_mock_message(MOCK_GAP_ANALYSIS),
        ]
        
        from src.analyser import full_analysis
        result = full_analysis("CV text here", "Job description here")
        
        assert "job_skills" in result
        assert "candidate_skills" in result
        assert "gap_analysis" in result
