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
1. User Opens a Website
The process begins when the user visits a website in the browser and requests an analysis.
2. Webpage Information Collection
The system collects important information from the webpage, including the URL, webpage title, visible text, password fields, number of forms, external links, HTTPS status, and meta description. 
3. Data Processing and Feature Extraction
The collected information is organized into a structured format so that it can be analyzed consistently.
4. Phishing Analysis
The system examines multiple indicators associated with phishing, including URL structure, domain or brand impersonation, login forms, password requests, suspicious links, urgent language, webpage content, forms, and external links. 
5. Website Classification
Based on the available evidence, the website is classified into one of three categories:
•	Safe 
•	Suspicious 
•	Phishing 
The system is designed to consider multiple indicators rather than deciding that a website is phishing based on only one characteristic. 
6. Risk and Confidence Score Generation
Along with the classification, the system produces a risk score and confidence score, both represented on a 0–100 scale. 
7. Result and Reason Display
Finally, the classification, risk level, confidence level, and supporting reasons are presented to the user. This allows the user to understand not only the result but also the factors contributing to the assessment. 
 


### Disclaimer

PhishGuard AI is intended as a cybersecurity research and educational project. Its predictions are assessments and should not be treated as a guarantee that a website is safe or malicious.

