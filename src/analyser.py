"""
analyser.py
-----------
Core analysis logic. Uses the Google Gemini API (free tier) to:
  1. Extract required skills from a job description
  2. Extract skills the candidate has from their CV
  3. Perform gap analysis and return structured results
"""

import json
import os
import urllib.request


# ── Config ─────────────────────────────────────────────────────────────────────
# Free model — 1,500 requests/day, no credit card needed
MODEL = "gemini-1.5-flash"
API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


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
Return ONLY valid JSON, no explanation text, no markdown backticks."""


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

Return ONLY valid JSON, no explanation text, no markdown backticks."""


GAP_ANALYSIS_PROMPT = """You are a career coach specialising in data science roles.

Compare the candidate's skills against the job requirements and provide actionable guidance.

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

Be honest but constructive. Return ONLY valid JSON, no explanation text, no markdown backticks."""


# ── Core helper ────────────────────────────────────────────────────────────────

def _call_gemini(prompt: str) -> dict:
    """
    Call the Gemini API and return parsed JSON.
    Uses urllib (built into Python) — no extra library needed.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found. Add it to your .env file.")

    url = f"{API_BASE}/{MODEL}:generateContent?key={api_key}"

    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.1,          # Low temperature = more consistent JSON
            "responseMimeType": "application/json"  # Forces JSON output
        }
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode("utf-8"))

    # Extract the text from Gemini's response structure
    raw_text = result["candidates"][0]["content"]["parts"][0]["text"]

    # Strip markdown fences if present (safety net)
    raw_text = raw_text.strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]

    return json.loads(raw_text.strip())


# ── Public functions ───────────────────────────────────────────────────────────

def extract_job_skills(job_description: str) -> dict:
    prompt = EXTRACTION_PROMPT.format(job_description=job_description)
    return _call_gemini(prompt)


def extract_cv_skills(cv_text: str) -> dict:
    prompt = CV_SKILLS_PROMPT.format(cv_text=cv_text)
    return _call_gemini(prompt)


def run_gap_analysis(job_skills: dict, candidate_skills: dict) -> dict:
    prompt = GAP_ANALYSIS_PROMPT.format(
        job_skills_json=json.dumps(job_skills, indent=2),
        candidate_skills_json=json.dumps(candidate_skills, indent=2)
    )
    return _call_gemini(prompt)


def full_analysis(cv_text: str, job_description: str) -> dict:
    """Run the complete 3-step pipeline: JD → CV → Gap analysis."""
    job_skills = extract_job_skills(job_description)
    candidate_skills = extract_cv_skills(cv_text)
    gap_analysis = run_gap_analysis(job_skills, candidate_skills)

    return {
        "job_skills": job_skills,
        "candidate_skills": candidate_skills,
        "gap_analysis": gap_analysis
    }
