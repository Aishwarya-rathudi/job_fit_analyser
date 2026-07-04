# 🎯 Job Fit Analyser — AI-Powered CV Match Tool

> Upload your CV, paste a job description, and get an instant AI-powered analysis of your fit — with a match score, skill gap breakdown, and personalised learning roadmap.

🔗 **[Live Demo](https://aishwarya-job-fit-analyser.streamlit.app)** &nbsp;|&nbsp; 👩‍💻 **[Portfolio](https://aishwarya-portfolio.site)** &nbsp;|&nbsp; 💼 **[LinkedIn](https://www.linkedin.com/in/aishwarya-rathudi/)**

---

## 📸 App Preview

![Job Fit Analyser Screenshot](c:\Users\rathu\Desktop\Screenshot-job-fit-analyser app.png)


> 💡 **Tip:** Replace the image above with a real screenshot. Take one with your app running, upload it to your GitHub repo as `screenshot.png`, and update this link.

---

## ✨ What It Does

Most job seekers apply blindly and wonder why they don't hear back. This tool changes that.

Paste any job description + upload your CV → the app uses **Llama 3.3 70B via Groq** to:

- 📊 **Score your fit** — 0 to 100% match against the role
- ✅ **Show matched skills** — what you already have that the employer wants
- ❌ **Identify skill gaps** — must-haves vs nice-to-haves you're missing
- 📚 **Recommend resources** — specific courses to close each gap
- 📅 **Build a learning timeline** — estimated weeks to become fully qualified
- 🎤 **Generate interview talking points** — tailored to this specific role

---

## 🧠 How the RAG Pattern Works

This app uses **Retrieval-Augmented Generation (RAG)** — a technique where external documents are injected as context into an LLM prompt, rather than relying on the model's training data alone.

```
┌──────────────┐     ┌────────────────────┐
│   Your CV    │     │  Job Description   │
│ (PDF / DOCX) │     │  (pasted text)     │
└──────┬───────┘     └────────┬───────────┘
       │                      │
       ▼                      ▼
┌─────────────────────────────────────────┐
│         Text Extraction Layer           │
│  pdfplumber / python-docx               │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│        Groq API — 3 LLM Calls           │
│                                         │
│  Call 1: Extract skills from JD  →JSON  │
│  Call 2: Extract skills from CV  →JSON  │
│  Call 3: Gap analysis & scoring  →JSON  │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│    Streamlit Dashboard + Plotly Charts  │
│  Gauge · Bar chart · Timeline · Tips    │
└─────────────────────────────────────────┘
```

---

## 🗂️ Project Structure

```
job_fit_analyser/
│
├── app.py                  # Streamlit UI — layout, inputs, results display
│
├── src/
│   ├── analyser.py         # Core RAG logic — Groq API calls & prompt templates
│   ├── cv_parser.py        # Extracts text from PDF and DOCX uploads
│   └── charts.py           # Plotly visualisations (gauge, bar, timeline)
│
├── tests/
│   └── test_analyser.py    # Unit tests with mocked API responses
│
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
└── README.md               # This file
```

---

## 🚀 Run It Locally

### Prerequisites
- Python 3.10+
- A free Groq API key from [console.groq.com](https://console.groq.com)

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/job-fit-analyser.git
cd job-fit-analyser

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API key
cp .env.example .env
# Open .env and paste your Groq key: GROQ_API_KEY=gsk_...

# 5. Run
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

---

## 🌐 Deployment

Deployed on **Streamlit Cloud** (free tier).

To deploy your own copy:
1. Fork this repo
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app** → select your fork
3. In **Advanced settings → Secrets**, add:
```toml
GROQ_API_KEY = "gsk_your_key_here"
```
4. Click **Deploy** — live in ~2 minutes

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| **Python** | Core language |
| **Groq API** (Llama 3.3 70B) | LLM for skill extraction and gap analysis |
| **Streamlit** | Web app framework |
| **pdfplumber** | PDF text extraction |
| **python-docx** | DOCX text extraction |
| **Plotly** | Interactive charts |
| **python-dotenv** | Environment variable management |

---

## 💡 Key Technical Decisions

**Why Groq?** Groq's LPU hardware makes inference 10x faster than traditional GPU-based APIs, and the free tier (14,400 requests/day) is sufficient for a production tool. Llama 3.3 70B also produces more reliable structured JSON output than smaller models.

**Why 3 separate LLM calls instead of 1?** Breaking the task into focused steps (extract JD skills → extract CV skills → compare) produces significantly more accurate results than asking the model to do everything in one prompt. Each call has a clear, narrow task.

**Why `response_format: json_object`?** Enforcing JSON output at the API level eliminates parsing failures from markdown-wrapped responses, making the app more reliable in production.

---

## 🔮 Future Improvements

- [ ] Multi-job comparison — analyse 3 roles at once and rank by fit
- [ ] CV rewriter — auto-improve your bullet points to match the JD
- [ ] Salary estimator — pull market rates for each role via web search
- [ ] Export to PDF — download your gap analysis as a study plan
- [ ] Job URL input — auto-fetch JD from a LinkedIn or Indeed link

---

## 👩‍💻 Author

**Aishwarya Rathudi** — Data Scientist based in Dublin, Ireland

MSc Data Analytics · Python · Machine Learning · MLOps · AWS · Azure

[![Portfolio](https://img.shields.io/badge/Portfolio-Visit-blue)](https://aishwarya-portfolio.site)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5)](https://linkedin.com/in/YOUR_LINKEDIN)

---

## 📄 Licence

MIT — feel free to fork, adapt, and build on this project.
