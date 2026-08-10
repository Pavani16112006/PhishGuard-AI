import json
import os
from pathlib import Path

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

from prompt import SYSTEM_PROMPT


# Load .env
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)

hf_token = os.getenv("HF_TOKEN")

if not hf_token:
    raise RuntimeError("HF_TOKEN was not found in .env")


client = InferenceClient(
    api_key=hf_token
)


def analyze(site):

    user_prompt = f"""
Analyze this website for phishing.

URL:
{site.url}

Title:
{site.title}

Visible Text:
{site.text}

Password Field:
{site.hasPasswordField}

Forms:
{site.forms}

External Links:
{site.externalLinks}

HTTPS:
{site.isHttps}

Meta Description:
{site.metaDescription}
"""

    response = client.chat_completion(
        model="Qwen/Qwen2.5-7B-Instruct",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        max_tokens=500,
        temperature=0.1
    )

    output = response.choices[0].message.content.strip()

    try:
        return json.loads(output)

    except json.JSONDecodeError:

        return {
            "prediction": "Unknown",
            "risk": 50,
            "confidence": 0,
            "reasons": [
                "The AI returned an unexpected response."
            ],
            "raw_response": output
        }