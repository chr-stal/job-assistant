import json
from fastapi import FastAPI
from anthropic import Anthropic
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

app = FastAPI()
client = Anthropic()

class AnalysisRequest(BaseModel):
    resume: str
    job_description: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/analyze")
def analyze(request: AnalysisRequest):
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
    return parsed

class CoverLetterRequest(BaseModel):
    resume: str
    job_description: str
    tone: str = "professional"

@app.post("/cover-letter")
def cover_letter(request: CoverLetterRequest):
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
    return parsed