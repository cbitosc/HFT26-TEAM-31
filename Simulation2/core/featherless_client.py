"""
core/featherless_client.py - Secure Featherless API integration for LLM reasoning.
Handles authentication, request formatting, timeout management, and JSON extraction.
"""

import os
import json
import re
import requests
from dotenv import load_dotenv

# Load environment variables from .env file if available
load_dotenv()

URL = "https://api.featherless.ai/v1/chat/completions"
MODEL = "meta-llama/Meta-Llama-3.1-70B-Instruct"


def get_api_key() -> str:
    """Safely retrieves the Featherless API key from environment variables."""
    return os.getenv("FEATHERLESS_API_KEY", "").strip()


def call_featherless(system_prompt: str, user_prompt: str, temp: float = 0.7) -> str:
    """
    Calls the Featherless API with the given system and user prompts.
    Raises Exception("NO_KEY") if the API key is not configured.
    """
    api_key = get_api_key()
    if not api_key or api_key == "your_key_here":
        raise Exception("NO_KEY")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    body = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": temp,
        "max_tokens": 1200
    }

    response = requests.post(URL, headers=headers, json=body, timeout=30)
    response.raise_for_status()
    payload = response.json()
    return payload["choices"][0]["message"]["content"]


def extract_json(raw_text: str) -> dict:
    """
    Robust JSON parser that extracts JSON objects even when wrapped in
    markdown code blocks (```json ... ```) or accompanied by explanatory text.
    """
    clean_text = raw_text.strip()
    
    # Strip markdown code fence if present
    if "```" in clean_text:
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", clean_text, re.DOTALL)
        if match:
            clean_text = match.group(1)
        else:
            # Fallback: extract the outermost {...}
            match = re.search(r"(\{.*\})", clean_text, re.DOTALL)
            if match:
                clean_text = match.group(1)
    else:
        match = re.search(r"(\{.*\})", clean_text, re.DOTALL)
        if match:
            clean_text = match.group(1)

    return json.loads(clean_text)

