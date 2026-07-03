"""
analyser.py
-----------
Core analysis logic using Groq API (free tier).
Uses the official groq Python library to avoid Cloudflare blocks.
"""

import json
import os
from groq import Groq


MODEL = "llama-3.3-70b-versatile"


# ── Prompts ───────────────────────────────────────────────────────────────────

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

Compare the candidate skills against the job requirements and provide actionable guidance.

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

Return ONLY valid JSON, no explanation text, no markdown backticks."""


# ── Core helper ────────────────────────────────────────────────────────────────

def _call_groq(prompt: str) -> dict:
    """Call Groq using the official library and return parsed JSON."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found. Add it to your .env file.")

    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that always responds with valid JSON only. No markdown, no explanation, just raw JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1,
        max_tokens=3000,
        response_format={"type": "json_object"}
    )

    raw_text = response.choices[0].message.content.strip()

    # Strip markdown fences if present (safety net)
    if raw_text.startswith("```"):
        lines = raw_text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        raw_text = "\n".join(lines).strip()

    return json.loads(raw_text)


# ── Public functions ───────────────────────────────────────────────────────────

def extract_job_skills(job_description: str) -> dict:
    prompt = EXTRACTION_PROMPT.format(job_description=job_description)
    return _call_groq(prompt)


def extract_cv_skills(cv_text: str) -> dict:
    prompt = CV_SKILLS_PROMPT.format(cv_text=cv_text)
    return _call_groq(prompt)


def run_gap_analysis(job_skills: dict, candidate_skills: dict) -> dict:
    prompt = GAP_ANALYSIS_PROMPT.format(
        job_skills_json=json.dumps(job_skills, indent=2),
        candidate_skills_json=json.dumps(candidate_skills, indent=2)
    )
    return _call_groq(prompt)


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
