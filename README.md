# Job Assistant API

An AI-powered backend API that analyzes resumes against job descriptions and generates tailored cover letters. Built with FastAPI and Claude AI.

## Live API
`https://job-assistant-production-03cd.up.railway.app`

## Features
- Resume analysis with match scoring against a job description
- Tailored cover letter generation with tone control
- Persistent storage of all analyses and cover letters
- Application history retrieval

## Tech Stack
- **FastAPI** — Python web framework
- **Claude API (Anthropic)** — AI analysis and generation
- **SQLAlchemy + SQLite** — database and ORM
- **Railway** — cloud deployment

## Running Locally

**1. Clone the repo**
```bash
git clone https://github.com/chr-stal/job-assistant.git
cd job-assistant
```

**2. Create and activate virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Add your API key**
```bash
touch .env
```
Inside `.env`:

ANTHROPIC_API_KEY=YOURKEY

**5. Run the server**
```bash
uvicorn main:app --reload
```

## API Endpoints

### Analyze Resume
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "resume": "Your resume text here",
    "job_description": "Job description here"
  }'
```

**Response:**
```json
{
  "id": 1,
  "match_score": 78,
  "strengths": ["..."],
  "gaps": ["..."],
  "summary": "..."
}
```

### Generate Cover Letter
```bash
curl -X POST http://localhost:8000/cover-letter \
  -H "Content-Type: application/json" \
  -d '{
    "resume": "Your resume text here",
    "job_description": "Job description here",
    "tone": "confident"
  }'
```

**Response:**
```json
{
  "id": 1,
  "subject": "...",
  "body": "...",
  "highlights": ["..."]
}
```

### Get History
```bash
curl http://localhost:8000/history
```

### Get Application by ID
```bash
curl http://localhost:8000/history/1
```