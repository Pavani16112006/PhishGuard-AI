from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def analyze(site):

    prompt = f"""
Analyze this website.

URL:
{site.url}

Title:
{site.title}

Text:
{site.text}

Return ONLY valid JSON in this format:

{{
  "prediction": "Safe or Phishing",
  "risk": 0,
  "confidence": 0,
  "reasons": []
}}
"""

    response = client.responses.create(
        model="gpt-5.5",
        input=prompt
    )

    return response.output_text
