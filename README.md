# 🎯 Job Fit Analyser — AI-Powered CV Match Tool

A RAG-based LLM application that analyses your CV against any job description using Claude AI, giving you a match score, skill gap analysis, and a personalised learning roadmap.

**Built with:** Python · Anthropic Claude · Streamlit · Plotly

---

## ✨ Features

- **CV parsing** — supports PDF and DOCX upload
- **AI skill extraction** — Claude reads both your CV and the job description and extracts structured skill data
- **Match score** — 0–100% fit score with visual gauge
- **Gap analysis** — categorised by must-have vs nice-to-have, with learning resources for each gap
- **Learning timeline** — estimated weeks to close each skill gap
- **Interview talking points** — Claude suggests how to frame your experience for this specific role

---

## 🗂️ Project Structure

```
job_fit_analyser/
│
├── app.py                  # Main Streamlit application (UI + orchestration)
│
├── src/
│   ├── cv_parser.py        # Extracts text from PDF/DOCX uploads
│   ├── analyser.py         # Core Claude API calls + prompt templates (RAG logic)
│   └── charts.py           # Plotly visualisation functions
│
├── tests/
│   └── test_analyser.py    # Unit tests
│
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
└── README.md               # This file
```

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/job-fit-analyser.git
cd job-fit-analyser
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Get your Anthropic API key
- Go to [console.anthropic.com](https://console.anthropic.com/)
- Sign up (free credits included)
- Create an API key

### 5. Set up your environment
```bash
cp .env.example .env
# Open .env and paste your API key
```

### 6. Run the app
```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`

---

## 🧠 How the RAG Pattern Works

This app uses **Retrieval-Augmented Generation (RAG)** — the technique of injecting external documents as context into an LLM prompt, rather than relying on the model's training data.

```
┌─────────────────┐     ┌───────────────────┐
│   Your CV       │     │  Job Description  │
│ (PDF/DOCX)      │     │  (pasted text)    │
└────────┬────────┘     └─────────┬─────────┘
         │                        │
         ▼                        ▼
┌────────────────────────────────────────────┐
│          Text Extraction Layer             │
│   cv_parser.py  │  raw job description     │
└────────────────────┬───────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────┐
│           Claude API (3 calls)             │
│                                            │
│  Call 1: Extract skills from JD → JSON    │
│  Call 2: Extract skills from CV → JSON    │
│  Call 3: Compare both → gap analysis      │
└────────────────────┬───────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────┐
│      Streamlit Dashboard + Plotly Charts   │
│   Match score · Gaps · Timeline · Tips     │
└────────────────────────────────────────────┘
```

---

## 🚢 Deployment (Free)

### Deploy to Streamlit Cloud
1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Add `ANTHROPIC_API_KEY` in the Secrets section
5. Deploy — you get a public URL instantly

### Deploy to Hugging Face Spaces
1. Create a new Space (select Streamlit SDK)
2. Upload all project files
3. Add `ANTHROPIC_API_KEY` in Space Settings → Repository secrets

---

## 🛠️ Extending This Project

Ideas to make it more impressive for your portfolio:

- **Multi-job comparison** — analyse 3 jobs at once and rank them by fit
- **CV improvement suggestions** — ask Claude to rewrite weak bullets to better match the JD
- **Salary estimation** — use web search tool to pull salary ranges for each role
- **Export to PDF** — download your gap analysis as a personalised study plan
- **Job board scraper** — auto-fetch job descriptions from LinkedIn or Indeed URLs

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `anthropic` | Claude API client |
| `streamlit` | Web app framework |
| `pdfplumber` | PDF text extraction |
| `python-docx` | DOCX text extraction |
| `plotly` | Interactive charts |
| `python-dotenv` | Load .env file |

---

## 👩‍💻 Author

**Aishwarya Rathudi** — Data Scientist  
[Portfolio](https://aishwarya-portfolio.site) · [LinkedIn](#) · [GitHub](#)
