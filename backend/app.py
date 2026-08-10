from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ai import analyze

app = FastAPI(title="PhishGuard AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Website(BaseModel):
    url: str
    title: str
    text: str
    hasPasswordField: bool
    forms: int
    externalLinks: int
    isHttps: bool
    metaDescription: str


@app.get("/")
def home():
    return {
        "status": "Backend Running"
    }


@app.post("/analyze")
def analyze_site(site: Website):
    return analyze(site)