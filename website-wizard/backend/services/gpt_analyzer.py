import json
import os
import logging
from typing import Dict, Any

from openai import OpenAI

# Initialize client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

logger = logging.getLogger(__name__)


def safe_json_loads(content: str) -> Dict[str, Any]:
    """
    Safely parse JSON from GPT response.
    Prevents crashes if model returns invalid JSON.
    """
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        logger.error("Invalid JSON from GPT. Raw content: %s", content)
        return {
            "summary": "Analysis failed due to formatting error.",
            "top_issues": [],
            "quick_wins": [],
            "strengths": [],
        }


def truncate_data(data: dict, max_length: int = 5000) -> str:
    """
    Prevent prompt from becoming too large.
    """
    text = json.dumps(data, ensure_ascii=False)
    return text[:max_length]


def analyze_website(
    url: str,
    crawl_data: dict,
    lighthouse_data: dict
) -> Dict[str, Any]:
    """
    Analyze website using GPT with structured output.
    """

    lighthouse_summary = {
        "performance_score": lighthouse_data.get("performance_score"),
        "seo_score": lighthouse_data.get("seo_score"),
        "accessibility_score": lighthouse_data.get("accessibility_score"),
        "best_practices_score": lighthouse_data.get("best_practices_score"),
    }

    prompt = f"""
You are an expert website auditor.

Analyze this website data and return ONLY valid JSON with this schema:
{{
  "summary": "string",
  "top_issues": [
    {{
      "category": "seo|performance|accessibility|ux|content|best_practices",
      "issue": "string",
      "severity": "low|medium|high",
      "recommendation": "string"
    }}
  ],
  "quick_wins": ["string"],
  "strengths": ["string"]
}}

Website URL:
{url}

Crawl Data:
{truncate_data(crawl_data)}

Lighthouse Data:
{json.dumps(lighthouse_summary, ensure_ascii=False)}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            temperature=0.2,
            messages=[
                {"role": "system", "content": "Return only valid JSON."},
                {"role": "user", "content": prompt},
            ],
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError("Empty response from GPT")

        return safe_json_loads(content)

    except Exception as e:
        logger.error("GPT analysis failed: %s", str(e))

        # 🔥 Fallback response (prevents API crash)
        return {
            "summary": "Analysis temporarily unavailable.",
            "top_issues": [],
            "quick_wins": [],
            "strengths": [],
        }