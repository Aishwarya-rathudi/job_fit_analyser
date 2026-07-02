"""
analyser.py
-----------
Core analysis logic. Uses the OpenAI API to:
  1. Extract required skills from a job description
  2. Extract skills the candidate has from their CV
  3. Perform gap analysis and return structured results

This is the RAG-style pattern:
  - The "context" (CV text + job description) is injected into each prompt
  - GPT reasons over that context to produce structured JSON output
"""

import json
import openai
import os


# ── Initialise the OpenAI client ──────────────────────────────────────────────
# Reads OPENAI_API_KEY from your environment / .env automatically
client = openai.OpenAI()

MODEL = "gpt-4o"  # Best reasoning for structured analysis; use "gpt-3.5-turbo" for lower cost


# ── Prompt templates ──────────────────────────────────────────────────────────

EXTRACTION_PROMPT = """You are an expert technical recruiter and data science hiring specialist.

Analyse the following job description and extract ALL required and preferred skills.

JOB DESCRIPTION:
{job_description}

Return your response as a valid JSON object with this exact structure:
{{
  "job_title": "extracted job title or 'Data Scientist' if not clear",
  "company": "company name if mentioned, else 'Not specified'",
  "required_skills": [
    {{
      "skill": "skill name",
      "category": "one of: Programming, Machine Learning, MLOps, Cloud, Data Engineering, Visualization, Soft Skills, Domain Knowledge",
      "importance": "must-have or nice-to-have"
    }}
  ],
  "experience_years": "e.g. '2-4 years' or 'Not specified'",
  "key_responsibilities": ["responsibility 1", "responsibility 2"]
}}

Be thorough. Extract every technical skill, tool, framework, methodology, and soft skill mentioned.
Return ONLY valid JSON, no explanation text."""


CV_SKILLS_PROMPT = """You are an expert CV analyser for data science roles.

Extract ALL skills and experiences from this CV text.

CV TEXT:
{cv_text}

Return your response as a valid JSON object with this exact structure:
{{
  "candidate_name": "name from CV",
  "education": "highest relevant degree",
  "total_experience_years": "estimated total relevant experience in years as a number",
  "skills": [
    {{
      "skill": "skill name",
      "category": "one of: Programming, Machine Learning, MLOps, Cloud, Data Engineering, Visualization, Soft Skills, Domain Knowledge",
      "proficiency": "one of: Expert, Proficient, Familiar",
      "evidence": "brief note on where/how this was demonstrated"
    }}
  ]
}}

Return ONLY valid JSON, no explanation text."""


GAP_ANALYSIS_PROMPT = """You are a career coach specialising in data science roles.

A candidate is applying for a data science position. Compare their skills against the job requirements and provide actionable guidance.

JOB REQUIREMENTS (JSON):
{job_skills_json}

CANDIDATE SKILLS (JSON):
{candidate_skills_json}

Return your response as a valid JSON object with this exact structure:
{{
  "overall_match_score": <integer 0-100>,
  "match_summary": "2-3 sentence honest summary of fit",
  "matched_skills": [
    {{
      "skill": "skill name",
      "category": "category",
      "candidate_level": "proficiency level"
    }}
  ],
  "gap_skills": [
    {{
      "skill": "skill name",
      "category": "category",
      "importance": "must-have or nice-to-have",
      "learning_resource": "specific course, book, or project to close this gap",
      "estimated_time": "e.g. '2 weeks', '1 month'"
    }}
  ],
  "strengths": ["strength 1", "strength 2", "strength 3"],
  "quick_wins": ["action 1", "action 2", "action 3"],
  "interview_talking_points": ["point 1", "point 2", "point 3"]
}}

Be honest but constructive. Return ONLY valid JSON, no explanation text."""


# ── Helper ─────────────────────────────────────────────────────────────────────

def _call_openai(prompt: str, max_tokens: int = 2000) -> dict:
    """
    Make a single OpenAI API call and return parsed JSON.
    Uses response_format=json_object to guarantee valid JSON back.
    """
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=max_tokens,
        response_format={"type": "json_object"},  # Forces valid JSON output
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that always responds with valid JSON only."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    response_text = response.choices[0].message.content
    return json.loads(response_text)


# ── Core functions ─────────────────────────────────────────────────────────────

def extract_job_skills(job_description: str) -> dict:
    """
    Send the job description to GPT and extract structured skills data.

    Args:
        job_description: Raw text of the job posting

    Returns:
        Dictionary with job title, required skills, responsibilities etc.
    """
    prompt = EXTRACTION_PROMPT.format(job_description=job_description)
    return _call_openai(prompt, max_tokens=2000)


def extract_cv_skills(cv_text: str) -> dict:
    """
    Send the CV text to GPT and extract structured skills data.

    Args:
        cv_text: Raw text extracted from the candidate's CV

    Returns:
        Dictionary with candidate name, skills, experience etc.
    """
    prompt = CV_SKILLS_PROMPT.format(cv_text=cv_text)
    return _call_openai(prompt, max_tokens=2000)


def run_gap_analysis(job_skills: dict, candidate_skills: dict) -> dict:
    """
    Compare job requirements against candidate skills to produce gap analysis.

    Args:
        job_skills: Output from extract_job_skills()
        candidate_skills: Output from extract_cv_skills()

    Returns:
        Dictionary with match score, gaps, strengths, and recommendations
    """
    prompt = GAP_ANALYSIS_PROMPT.format(
        job_skills_json=json.dumps(job_skills, indent=2),
        candidate_skills_json=json.dumps(candidate_skills, indent=2)
    )
    return _call_openai(prompt, max_tokens=3000)


def full_analysis(cv_text: str, job_description: str) -> dict:
    """
    Run the complete 3-step analysis pipeline.

    Steps:
      1. Extract skills from job description
      2. Extract skills from CV
      3. Run gap analysis comparing both

    Args:
        cv_text: Extracted text from the candidate's CV
        job_description: Raw text of the job posting

    Returns:
        Dictionary containing all three result sets
    """
    job_skills = extract_job_skills(job_description)
    candidate_skills = extract_cv_skills(cv_text)
    gap_analysis = run_gap_analysis(job_skills, candidate_skills)

    return {
        "job_skills": job_skills,
        "candidate_skills": candidate_skills,
        "gap_analysis": gap_analysis
    }
