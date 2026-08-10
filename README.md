# PhishGuard AI
## Overview

PhishGuard AI is an AI-powered browser extension designed to help users identify potentially malicious and phishing URLs before they visit dangerous websites.
The project combines a Chrome browser extension with a Python FastAPI backend that analyzes suspicious URLs using AI-based detection.

## Features

Analyze URLs for potential phishing threats
AI-assisted phishing detection
Chrome browser extension
HuggingFace model backend
Warn users about suspicious websites
Keeps sensitive environment variables out of Git
Communication between the browser extension and local backend

## Project Structure

PhishGuard-AI/ │ ├── backend/ │ ├── app.py │ ├── ai.py │ ├── prompt.py │ ├── requirements.txt │ └── .env # Not committed to Git │ ├── extension/ │ ├── background.js │ ├── content.js │ ├── manifest.json │ ├── popup.css │ ├── popup.html │ └── popup.js │ ├── .gitignore └── README.md
