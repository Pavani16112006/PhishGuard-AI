from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from ai import analyze

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Website(BaseModel):
    url: str
    title: str
    text: str

@app.post("/analyze")
def analyze_website(site: Website):
    result = analyze(site)
    return {"result": result}
