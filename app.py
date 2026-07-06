"""
app.py
------
Job Fit Analyser — Main Streamlit Application

A RAG-powered tool that:
  1. Takes your CV (PDF or DOCX) and a job description
  2. Uses Claude AI to extract and compare skills
  3. Shows match score, gaps, and a personalised learning roadmap

Run with:
    streamlit run app.py
"""

import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Local modules
from src.cv_parser import parse_cv
from src.analyser import full_analysis
from src.charts import match_score_gauge, skills_breakdown_chart, learning_timeline_chart


# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Job Fit Analyser | AI-Powered CV Match",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1F4E79, #2E75B6);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        border: 1px solid #E3F2FD;
        border-left: 4px solid #2E75B6;
        padding: 1rem 1.2rem;
        border-radius: 8px;
        margin-bottom: 0.8rem;
    }
    .skill-matched {
        background: #E8F5E9;
        border-left: 4px solid #4CAF50;
        padding: 0.5rem 0.8rem;
        border-radius: 6px;
        margin-bottom: 0.4rem;
        font-size: 0.9rem;
    }
    .skill-gap-must {
        background: #FFEBEE;
        border-left: 4px solid #F44336;
        padding: 0.5rem 0.8rem;
        border-radius: 6px;
        margin-bottom: 0.4rem;
        font-size: 0.9rem;
    }
    .skill-gap-nice {
        background: #FFF8E1;
        border-left: 4px solid #FF9800;
        padding: 0.5rem 0.8rem;
        border-radius: 6px;
        margin-bottom: 0.4rem;
        font-size: 0.9rem;
    }
    .talking-point {
        background: #E3F2FD;
        border-left: 4px solid #1F4E79;
        padding: 0.6rem 0.8rem;
        border-radius: 6px;
        margin-bottom: 0.4rem;
    }
    .stButton > button {
        background: linear-gradient(135deg, #1F4E79, #2E75B6);
        color: white;
        border: none;
        padding: 0.7rem 2rem;
        font-size: 1.1rem;
        font-weight: bold;
        border-radius: 8px;
        width: 100%;
    }
    .stButton > button:hover {
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🎯 Job Fit Analyser</h1>
    <p style="font-size: 1.1rem; opacity: 0.9; margin: 0;">
        AI-powered CV match analysis · Skill gap detection · Personalised learning roadmap
    </p>
</div>
""", unsafe_allow_html=True)


# ── Sidebar: API key ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    
    api_key = os.getenv("GROQ_API_KEY", "")
    
    if not api_key:
        api_key = st.text_input(
            "Groq API Key",
            type="password",
            help="Get your key at console.groq.com",
            placeholder="gsk_..."
        )
        if api_key:
            os.environ["GROQ_API_KEY"] = api_key
            st.success("✅ API key set!")
    else:
        st.success("✅ API key loaded from .env")
    
    if os.getenv("GROQ_API_KEY"):
        key = os.getenv("GROQ_API_KEY")
        if not key.startswith("gsk_"):
            st.warning("⚠️ Key looks wrong — Groq keys start with 'gsk_'")
    
    st.markdown("---")
    st.markdown("### 📖 How It Works")
    st.markdown("""
    1. **Upload your CV** (PDF or DOCX)
    2. **Paste a job description**
    3. **Click Analyse** 
    4. **Review your results** — match score, gaps, and your learning roadmap
    
    
    """)


# ── Main Input Section ────────────────────────────────────────────────────────
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### 📄 Your CV")
    uploaded_cv = st.file_uploader(
        "Upload your CV",
        type=["pdf", "docx"],
        help="PDF or Word document accepted",
        label_visibility="collapsed"
    )
    
    if uploaded_cv:
        st.success(f"✅ Uploaded: **{uploaded_cv.name}**")

with col2:
    st.markdown("### 📋 Job Description")
    job_description = st.text_area(
        "Paste the job description here",
        height=220,
        placeholder="Paste the full job description here — the more detail, the better the analysis...",
        label_visibility="collapsed"
    )
    if job_description:
        word_count = len(job_description.split())
        st.caption(f"📝 {word_count} words — {'Good detail' if word_count > 100 else 'Add more detail for better results'}")


# ── Analyse Button ─────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)

ready = uploaded_cv is not None and len(job_description.strip()) > 50 and os.getenv("GROQ_API_KEY")

if not ready:
    if not os.getenv("GROQ_API_KEY"):
        st.warning("⚠️ Add your OpenAI API key in the sidebar to get started.")
    elif not uploaded_cv:
        st.info("👆 Upload your CV and paste a job description to begin.")

analyse_clicked = st.button(
    "🎯 Analyse My Fit",
    disabled=not ready,
    use_container_width=True
)


# ── Analysis & Results ────────────────────────────────────────────────────────
if analyse_clicked and ready:
    
    # Step 1: Parse CV
    with st.spinner("📄 Reading your CV..."):
        try:
            cv_text = parse_cv(uploaded_cv)
            if len(cv_text.strip()) < 100:
                st.error("⚠️ Could not extract enough text from your CV. Try a different format.")
                st.stop()
        except Exception as e:
            st.error(f"Error reading CV: {e}")
            st.stop()
    
    # Step 2: Run full AI analysis
    with st.spinner("🤖 Analysing your profile against the job requirements... (this takes ~15 seconds)"):
        try:
            results = full_analysis(cv_text, job_description)
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.stop()
    
    # Store in session state so results persist on re-run
    st.session_state["results"] = results
    st.success("✅ Analysis complete!")


# ── Display Results ────────────────────────────────────────────────────────────
if "results" in st.session_state:
    results = st.session_state["results"]
    job_data = results["job_skills"]
    candidate_data = results["candidate_skills"]
    gap_data = results["gap_analysis"]
    
    st.markdown("---")
    
    # ── Row 1: Job title + score summary ──
    st.markdown(f"## 📊 Results for: {job_data.get('job_title', 'Data Scientist')} at {job_data.get('company', 'this company')}")
    
    col_score, col_summary = st.columns([1, 2], gap="large")
    
    with col_score:
        fig_gauge = match_score_gauge(gap_data.get("overall_match_score", 0))
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    with col_summary:
        st.markdown("#### 🔍 Match Summary")
        st.markdown(f"""
        <div class="metric-card">
            {gap_data.get('match_summary', '')}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("#### ⚡ Quick Wins — Do These First")
        for win in gap_data.get("quick_wins", []):
            st.markdown(f"""
            <div class="metric-card">
                ✅ {win}
            </div>
            """, unsafe_allow_html=True)
    
    # ── Row 2: Skills breakdown chart ──
    st.markdown("---")
    matched = gap_data.get("matched_skills", [])
    gaps = gap_data.get("gap_skills", [])
    
    fig_breakdown = skills_breakdown_chart(matched, gaps)
    st.plotly_chart(fig_breakdown, use_container_width=True)
    
    # ── Row 3: Matched skills + Gaps side by side ──
    col_matched, col_gaps = st.columns([1, 1], gap="large")
    
    with col_matched:
        st.markdown(f"### ✅ Skills You Have ({len(matched)})")
        for skill in matched:
            st.markdown(f"""
            <div class="skill-matched">
                <strong>{skill.get('skill')}</strong>
                <span style="color: #555; float: right;">{skill.get('category', '')}</span>
            </div>
            """, unsafe_allow_html=True)
    
    with col_gaps:
        must_gaps = [g for g in gaps if g.get("importance") == "must-have"]
        nice_gaps = [g for g in gaps if g.get("importance") != "must-have"]
        
        st.markdown(f"### ❌ Must-Have Gaps ({len(must_gaps)})")
        for gap in must_gaps:
            st.markdown(f"""
            <div class="skill-gap-must">
                <strong>{gap.get('skill')}</strong><br>
                <small>📚 {gap.get('learning_resource', 'Search online courses')} · ⏱ {gap.get('estimated_time', 'TBD')}</small>
            </div>
            """, unsafe_allow_html=True)
        
        if nice_gaps:
            st.markdown(f"### ⚠️ Nice-to-Have Gaps ({len(nice_gaps)})")
            for gap in nice_gaps:
                st.markdown(f"""
                <div class="skill-gap-nice">
                    <strong>{gap.get('skill')}</strong>
                    <span style="color: #888; float: right;">⏱ {gap.get('estimated_time', 'TBD')}</span>
                </div>
                """, unsafe_allow_html=True)
    
    # ── Row 4: Learning timeline ──
    st.markdown("---")
    st.markdown("### 📅 Your Learning Roadmap")
    fig_timeline = learning_timeline_chart(gaps)
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    # ── Row 5: Strengths + interview talking points ──
    col_str, col_interview = st.columns([1, 1], gap="large")
    
    with col_str:
        st.markdown("### 💪 Your Strengths for This Role")
        for strength in gap_data.get("strengths", []):
            st.markdown(f"""
            <div class="metric-card">
                ⭐ {strength}
            </div>
            """, unsafe_allow_html=True)
    
    with col_interview:
        st.markdown("### 🎤 Interview Talking Points")
        st.caption("Use these to frame your answers around what this employer values most")
        for point in gap_data.get("interview_talking_points", []):
            st.markdown(f"""
            <div class="talking-point">
                💬 {point}
            </div>
            """, unsafe_allow_html=True)
    
    # ── Row 6: Raw data expander ──
    with st.expander("🔧 View Raw Analysis Data (for debugging / portfolio demo)"):
        st.json(results)
