import json
import os
import re
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from prompt import SYSTEM_PROMPT
# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)

hf_token = os.getenv("HF_TOKEN")

if not hf_token:
    raise RuntimeError(
        f"HF_TOKEN was not found in .env\n"
        f"Expected .env at: {env_path}"
    )

# ============================================================
# HUGGING FACE CLIENT
# ============================================================

client = InferenceClient(
    api_key=hf_token
)
# ============================================================
# DEMO / TEST PHISHING DOMAIN OVERRIDES
# ============================================================
#
# IMPORTANT:
# Put ONLY domains that you have selected for your course/demo
# testing here.
#
# These domains will always receive at least:
#
#       Risk >= 60%
#       Prediction >= Suspicious
#
# Subdomains are also detected.
#
# Example:
#
#   example-phishing.test
#
# will also match:
#
#   login.example-phishing.test
#   secure.example-phishing.test
#
# ============================================================
DEMO_PHISHING_DOMAINS = {
    "example-phishing.test",
    "phishing-demo.test",
    "fake-login.test",
}
# ============================================================
# GET DOMAIN FROM URL
# ============================================================
def get_domain(url):
    """
    Extract hostname/domain from a URL.
    """
    if not url:
        return ""
    try:
        # Add scheme if missing
        parsed_url = urlparse(url)
        if not parsed_url.netloc:
            parsed_url = urlparse("https://" + url)
        hostname = parsed_url.hostname
        if hostname:
            return hostname.lower().strip(".")
    except Exception as e:
        print("WARNING: Could not extract domain:", e)
    return ""
# ============================================================
# CHECK DEMO PHISHING DOMAIN
# ============================================================
def is_demo_phishing_domain(url):
    """
    Returns True if the domain is explicitly configured
    in DEMO_PHISHING_DOMAINS.
    Exact domains and their subdomains are matched.
    """
    domain = get_domain(url)
    if not domain:
        return False
    for configured_domain in DEMO_PHISHING_DOMAINS:
        configured_domain = (
            configured_domain
            .lower()
            .strip()
            .strip(".")
        )
        if not configured_domain:
            continue
        # Exact match
        if domain == configured_domain:
            return True
        # Subdomain match
        if domain.endswith("." + configured_domain):
            return True
    return False
# ============================================================
# SAFE VALUE
# ============================================================
def safe_value(value, default="Not available"):
    """
    Convert missing/empty values into a safe readable value.
    """
    if value is None:
        return default
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return default
        return value
    return value
# ============================================================
# CLEAN MODEL OUTPUT
# ============================================================
def clean_model_output(output):
    """
    Clean Qwen model output.
    Handles:
    - <think>...</think>
    - Markdown code fences
    - Extra whitespace
    """
    if output is None:
        return ""
    if not isinstance(output, str):
        output = str(output)
    output = output.strip()
    # --------------------------------------------------------
    # Remove Qwen thinking section
    # --------------------------------------------------------
    output = re.sub(
        r"<think>.*?</think>",
        "",
        output,
        flags=re.DOTALL | re.IGNORECASE
    )
    output = output.strip()
    # --------------------------------------------------------
    # Remove Markdown code fences
    # --------------------------------------------------------
    if output.startswith("```"):
        lines = output.splitlines()
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        output = "\n".join(lines).strip()
    return output
# ============================================================
# EXTRACT JSON
# ============================================================
def clean_json_response(output):
    """
    Extract valid JSON from AI response.
    """
    if not output:
        return None
    output = clean_model_output(output)
    if not output:
        return None
    # --------------------------------------------------------
    # Attempt 1: Direct JSON
    # --------------------------------------------------------
    try:
        result = json.loads(output)
        if isinstance(result, dict):
            return result
    except (json.JSONDecodeError, TypeError):
        pass
    # --------------------------------------------------------
    # Attempt 2: Find JSON object inside text
    # --------------------------------------------------------
    start = output.find("{")
    end = output.rfind("}")
    if start != -1 and end != -1 and end > start:
        json_text = output[start:end + 1]
        try:
            result = json.loads(json_text)
            if isinstance(result, dict):
                return result
        except (json.JSONDecodeError, TypeError):
            pass
    return None
# ============================================================
# NORMALIZE AI RESULT
# ============================================================
def normalize_result(result):
    """
    Validate and normalize the AI result.
    """
    if not isinstance(result, dict):
        return None
    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------
    prediction = result.get("prediction")
    if isinstance(prediction, str):
        prediction = prediction.strip().lower()
        if prediction == "safe":
            prediction = "Safe"
        elif prediction == "suspicious":
            prediction = "Suspicious"
        elif prediction == "phishing":
            prediction = "Phishing"
        else:
            prediction = None
    else:
        prediction = None
    # --------------------------------------------------------
    # Risk
    # --------------------------------------------------------
    risk = result.get("risk", 50)
    try:
        risk = float(risk)
    except (ValueError, TypeError):
        risk = 50
    risk = max(0, min(100, risk))
    # --------------------------------------------------------
    # Confidence
    # --------------------------------------------------------
    confidence = result.get("confidence", 0)
    try:
        confidence = float(confidence)
    except (ValueError, TypeError):
        confidence = 0
    confidence = max(0, min(100, confidence))
    # --------------------------------------------------------
    # Reasons
    # --------------------------------------------------------
    reasons = result.get("reasons", [])
    if isinstance(reasons, str):
        reasons = [reasons]
    elif not isinstance(reasons, list):
        reasons = []
    reasons = [
        str(reason).strip()
        for reason in reasons
        if str(reason).strip()
    ]
    # --------------------------------------------------------
    # Prediction must be valid
    # --------------------------------------------------------
    if prediction is None:
        return None
    # --------------------------------------------------------
    # Convert whole-number floats
    # --------------------------------------------------------
    if risk.is_integer():
        risk = int(risk)
    if confidence.is_integer():
        confidence = int(confidence)
    return {
        "prediction": prediction,
        "risk": risk,
        "confidence": confidence,
        "reasons": reasons
    }
# ============================================================
# DEMO DOMAIN OVERRIDE
# ============================================================
def apply_demo_domain_override(result, site):
    """
    Apply the minimum risk rule for explicitly configured
    demonstration phishing domains.
    This does NOT automatically make every website phishing.
    It only affects domains listed in DEMO_PHISHING_DOMAINS.
    """
    url = str(
        getattr(site, "url", "") or ""
    )
    if not is_demo_phishing_domain(url):
        return result
    print(
        "DEMO DOMAIN MATCH:",
        get_domain(url)
    )
    # --------------------------------------------------------
    # Minimum risk = 60
    # --------------------------------------------------------
    current_risk = result.get("risk", 0)
    try:
        current_risk = float(current_risk)
    except (ValueError, TypeError):
        current_risk = 0
    result["risk"] = max(60, current_risk)
    # --------------------------------------------------------
    # Safe is not allowed for configured demo domains
    # --------------------------------------------------------
    if result.get("prediction") == "Safe":
        result["prediction"] = "Suspicious"
    # --------------------------------------------------------
    # If AI already says Phishing, keep Phishing.
    #
    # If AI says Suspicious, keep Suspicious.
    # --------------------------------------------------------
    if result.get("prediction") not in [
        "Suspicious",
        "Phishing"
    ]:
        result["prediction"] = "Suspicious"
    # --------------------------------------------------------
    # Minimum confidence for demo classification
    # --------------------------------------------------------
    current_confidence = result.get("confidence", 0)
    try:
        current_confidence = float(current_confidence)
    except (ValueError, TypeError):
        current_confidence = 0

    result["confidence"] = max(
        75,
        current_confidence
    )
    # --------------------------------------------------------
    # Add explanation
    # --------------------------------------------------------
    reasons = result.get("reasons", [])
    if not isinstance(reasons, list):
        reasons = [str(reasons)]
    reasons.append(
        "This domain is included in the configured phishing "
        "demonstration test list."
    )
    result["reasons"] = list(
        dict.fromkeys(
            str(reason).strip()
            for reason in reasons
            if str(reason).strip()
        )
    )
    # --------------------------------------------------------
    # Convert whole numbers
    # --------------------------------------------------------
    if isinstance(result["risk"], float):
        if result["risk"].is_integer():
            result["risk"] = int(result["risk"])
    if isinstance(result["confidence"], float):
        if result["confidence"].is_integer():
            result["confidence"] = int(result["confidence"])
    return result
# ============================================================
# FALLBACK ANALYSIS
# ============================================================
def fallback_analysis(site):
    """
    Local fallback analysis.
    Used when Hugging Face is unavailable or returns unusable
    output.
    This ensures the extension does not simply say:
    'No analysis'.
    """
    url = str(
        getattr(site, "url", "") or ""
    ).strip()
    title = str(
        getattr(site, "title", "") or ""
    ).strip()
    text = str(
        getattr(site, "text", "") or ""
    ).strip()
    url_lower = url.lower()
    title_lower = title.lower()
    text_lower = text.lower()
    reasons = []
    risk = 10
    # ========================================================
    # HTTPS
    # ========================================================
    is_https = getattr(
        site,
        "isHttps",
        None
    )
    if is_https is False:
        risk += 20
        reasons.append(
            "The website does not use HTTPS."
        )
    elif is_https is True:
        reasons.append(
            "The website uses HTTPS."
        )
    else:
        reasons.append(
            "HTTPS information was not available."
        )
    # ========================================================
    # Password field
    # ========================================================
    password_field = getattr(
        site,
        "hasPasswordField",
        None
    )
    if password_field is True:
        risk += 15
        reasons.append(
            "The page contains a password field."
        )
    # ========================================================
    # Forms
    # ========================================================
    forms = getattr(
        site,
        "forms",
        None
    )
    try:
        if forms:
            form_count = int(forms)
            if form_count > 0:
                risk += 5
                reasons.append(
                    f"The page contains {form_count} form(s)."
                )
    except (ValueError, TypeError):
        pass
    # ========================================================
    # Suspicious URL terms
    # ========================================================
    suspicious_url_terms = [
        "login",
        "signin",
        "sign-in",
        "verify",
        "verification",
        "secure",
        "account",
        "update",
        "password",
        "wallet",
        "payment",
        "confirm",
    ]
    matched_url_terms = [
        term
        for term in suspicious_url_terms
        if term in url_lower
    ]
    if matched_url_terms:
        risk += 10
        reasons.append(
            "The URL contains potentially sensitive terms: "
            + ", ".join(matched_url_terms)
        )
    # ========================================================
    # Urgent language
    # ========================================================
    urgent_terms = [
        "urgent",
        "immediately",
        "suspended",
        "suspension",
        "expire",
        "expired",
        "act now",
        "verify now",
        "limited time",
        "last warning",
    ]
    matched_urgent = [
        term
        for term in urgent_terms
        if term in title_lower or term in text_lower
    ]
    if matched_urgent:
        risk += 15
        reasons.append(
            "The webpage contains potentially urgent "
            "or threatening language."
        )
    # ========================================================
    # Payment information
    # ========================================================
    payment_terms = [
        "credit card",
        "debit card",
        "card number",
        "cvv",
        "cvc",
        "bank account",
        "payment",
        "billing",
    ]
    matched_payment = [
        term
        for term in payment_terms
        if term in text_lower
    ]
    if matched_payment:
        risk += 15
        reasons.append(
            "The webpage appears to request or discuss "
            "sensitive payment information."
        )
    # ========================================================
    # Credential harvesting
    # ========================================================
    credential_terms = [
        "enter your password",
        "enter password",
        "username and password",
        "verify your identity",
        "confirm your identity",
        "login credentials",
        "account credentials",
    ]
    matched_credentials = [
        term
        for term in credential_terms
        if term in text_lower
    ]
    if matched_credentials:
        risk += 20
        reasons.append(
            "The webpage contains language associated "
            "with credential collection."
        )
    # ========================================================
    # Risk limit
    # ========================================================
    risk = max(
        0,
        min(100, risk)
    )
    # ========================================================
    # Classification
    # ========================================================
    if risk >= 70:
        prediction = "Phishing"
    elif risk >= 40:
        prediction = "Suspicious"
    else:
        prediction = "Safe"
    # ========================================================
    # Very limited information
    # ========================================================
    if not url and not title and not text:
        prediction = "Suspicious"
        risk = 50
        reasons.append(
            "Very limited website information was available. "
            "The result should be treated cautiously."
        )
    # ========================================================
    # Ensure at least one reason
    # ========================================================
    if not reasons:
        reasons.append(
            "No strong phishing indicators were detected "
            "from the available website information."
        )
    return {
        "prediction": prediction,
        "risk": risk,
        "confidence": 35,
        "reasons": list(
            dict.fromkeys(reasons)
        )
    }
# ============================================================
# MAIN WEBSITE ANALYSIS
# ============================================================
def analyze(site):
    # ========================================================
    # COLLECT AVAILABLE WEBSITE INFORMATION
    # ========================================================
    url = safe_value(
        getattr(site, "url", None),
        "Not available"
    )
    title = safe_value(
        getattr(site, "title", None),
        "Not available"
    )
    text = safe_value(
        getattr(site, "text", None),
        "Not available"
    )
    password_field = safe_value(
        getattr(site, "hasPasswordField", None),
        "Not available"
    )
    forms = safe_value(
        getattr(site, "forms", None),
        "Not available"
    )
    external_links = safe_value(
        getattr(site, "externalLinks", None),
        "Not available"
    )
    https = safe_value(
        getattr(site, "isHttps", None),
        "Not available"
    )
    meta_description = safe_value(
        getattr(site, "metaDescription", None),
        "Not available"
    )
    # ========================================================
    # BUILD AI PROMPT
    # ========================================================
    user_prompt = f"""
Analyze this website for phishing.

IMPORTANT:

Some website information may be missing.

A missing field MUST NOT prevent analysis.

If a field says "Not available", ignore that field and continue
using all other available evidence.

Use whatever information is available.

Do NOT respond with "No analysis".

Do NOT refuse the analysis because information is incomplete.
Website information:
URL:
{url}
Title:
{title}
Visible Text:
{text}
Password Field:
{password_field}
Forms:
{forms}
External Links:
{external_links}
HTTPS:
{https}
Meta Description:
{meta_description}
Return ONLY valid JSON:
{{
    "prediction": "Safe",
    "risk": 0,
    "confidence": 0,
    "reasons": []
}}
"""
    # ========================================================
    # CALL HUGGING FACE
    # ========================================================
    try:
        response = client.chat_completion(
            model="Qwen/Qwen3-8B",
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
            max_tokens=700,
            temperature=0.1
        )
    except Exception as e:
        print(
            "ERROR: Hugging Face API request failed."
        )
        print(str(e))
        result = fallback_analysis(site)
        return apply_demo_domain_override(
            result,
            site
        )
    # ========================================================
    # EXTRACT MODEL RESPONSE
    # ========================================================
    try:
        output = None
        # ----------------------------------------------------
        # Object-style response
        # ----------------------------------------------------
        if hasattr(response, "choices"):
            choices = response.choices
            if choices:
                message = choices[0].message
                if hasattr(message, "content"):
                    output = message.content
                elif isinstance(message, dict):
                    output = message.get(
                        "content"
                    )
        # ----------------------------------------------------
        # Dictionary-style response
        # ----------------------------------------------------
        elif isinstance(response, dict):
            choices = response.get(
                "choices",
                []
            )
            if choices:

                message = choices[0].get(
                    "message",
                    {}
                )
                if isinstance(message, dict):

                    output = message.get(
                        "content"
                    )
        # ----------------------------------------------------
        # Debug output
        # ----------------------------------------------------
        print(
            "\n================ AI OUTPUT ================"
        )
        print(output)
        print(
            "===========================================\n"
        )
    except Exception as e:
        print(
            "WARNING: Could not extract AI response."
        )
        print(
            "Full response:",
            response
        )
        print(
            "Error:",
            str(e)
        )
        result = fallback_analysis(site)
        return apply_demo_domain_override(
            result,
            site
        )
    # ========================================================
    # EMPTY AI RESPONSE
    # ========================================================
    if not output:
        print(
            "WARNING: Model returned empty content."
        )
        result = fallback_analysis(site)
        return apply_demo_domain_override(
            result,
            site
        )
    # ========================================================
    # PARSE JSON
    # ========================================================
    result = clean_json_response(
        output
    )
    # ========================================================
    # NORMALIZE RESULT
    # ========================================================
    if result is not None:
        normalized = normalize_result(
            result
        )
        if normalized is not None:
            normalized = apply_demo_domain_override(
                normalized,
                site
            )
            return normalized
    # ========================================================
    # AI RESPONSE WAS INVALID
    # ========================================================
    print(
        "WARNING: AI response could not be parsed."
    )
    print(
        "RAW RESPONSE:"
    )
    print(output)
    # ========================================================
    # FALLBACK
    # ========================================================
    fallback = fallback_analysis(
        site
    )
    fallback = apply_demo_domain_override(
        fallback,
        site
    )
    return fallback
