from fastapi import FastAPI
from pydantic import BaseModel
from ai import analyze

app = FastAPI()

class Site(BaseModel):
    url:str
    title:str
    text:str

@app.post("/analyze")
def analyze_site(site:Site):
    return analyze(site)
