import json
from fastapi import FastAPI, Depends
from anthropic import Anthropic
from dotenv import load_dotenv
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, init_db, Application
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get("/")
def root():
    return FileResponse("static/index.html")

client = Anthropic()

init_db()

# get_db is a dependency that opens a database session per request and 
# closes it automatically when done — that's what Depends(get_db) is doing 
# in each endpoint.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class AnalysisRequest(BaseModel):
    resume: str
    job_description: str

class CoverLetterRequest(BaseModel):
    resume: str
    job_description: str
    tone: str = "professional"

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/analyze")
def analyze(request: AnalysisRequest, db: Session = Depends(get_db)):
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=2048,
        messages=[
            {
                "role": "user",
                "content": f"""You are an expert recruiter. Analyze this resume against the job description.

Resume:
{request.resume}

Job Description:
{request.job_description}

Return ONLY a raw JSON object with no markdown, no code blocks, no explanation. Just the JSON with exactly these fields:
- match_score: a number from 0-100
- strengths: list of 3 things the candidate does well for this role
- gaps: list of 3 things the candidate is missing
- summary: one sentence overview
"""
            }
        ]
    )
    parsed = json.loads(message.content[0].text)

    application = Application(
        resume=request.resume,
        job_description=request.job_description,
        match_score=parsed["match_score"],
        analysis=json.dumps(parsed)
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    return {**parsed, "id": application.id}

@app.post("/cover-letter")
def cover_letter(request: CoverLetterRequest, db: Session = Depends(get_db)):
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=2048,
        messages=[
            {
                "role": "user",
                "content": f"""You are an expert career coach. Write a tailored cover letter.

Resume:
{request.resume}

Job Description:
{request.job_description}

Tone: {request.tone}

Return ONLY a raw JSON object with no markdown, no code blocks. Just JSON with exactly these fields:
- subject: email subject line
- body: the full cover letter text
- highlights: list of 3 key selling points you emphasized
"""
            }
        ]
    )
    parsed = json.loads(message.content[0].text)

    application = Application(
        resume=request.resume,
        job_description=request.job_description,
        cover_letter=json.dumps(parsed)
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    # {**parsed, "id": application.id} spreads the parsed JSON 
    # and adds the database ID — so the caller knows what ID was 
    # assigned to their record.
    return {**parsed, "id": application.id}

@app.get("/history")
# returns a lightweight summary list, not the full records 
def history(db: Session = Depends(get_db)):
    applications = db.query(Application).order_by(Application.created_at.desc()).all()
    return [
        {
            "id": app.id,
            "match_score": app.match_score,
            "summary": json.loads(app.analysis)["summary"] if app.analysis else None,
            "has_cover_letter": app.cover_letter is not None,
            "created_at": app.created_at
        }
        for app in applications
    ]

@app.get("/history/{id}")
def get_application(id: int, db: Session = Depends(get_db)):
    application = db.query(Application).filter(Application.id == id).first()
    if not application:
        return {"error": "Application not found"}
    return {
        "id": application.id,
        "resume": application.resume,
        "job_description": application.job_description,
        "analysis": json.loads(application.analysis) if application.analysis else None,
        "cover_letter": json.loads(application.cover_letter) if application.cover_letter else None,
        "created_at": application.created_at
    }