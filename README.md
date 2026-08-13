# PhishGuard AI
## Overview

PhishGuard AI is an AI-powered browser extension designed to help users identify potentially malicious and phishing URLs before they visit dangerous websites.
The project combines a Chrome browser extension with an API backend that analyzes suspicious URLs using AI-based detection.

## Features

Analyze URLs for potential phishing threats

AI-assisted phishing detection

Chrome browser extension

HuggingFace model backend

Warn users about suspicious websites

Keeps sensitive environment variables out of Git

Communication between the browser extension and local backend

## Technologies

Python

Chrome Extensions (Manifest V3)

JavaScript, HTML, and CSS

Hugging Face Inference API

AI-based webpage analysis

## How It Works

The Chrome extension collects relevant information from the current webpage and sends it to the API backend. The backend passes this information to the AI model, which analyzes the webpage and returns a prediction, risk score, confidence level, and reasons.

### Disclaimer

PhishGuard AI is intended as a cybersecurity research and educational project. Its predictions are assessments and should not be treated as a guarantee that a website is safe or malicious.

