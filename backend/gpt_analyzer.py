import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analyze_audit(url: str, crawl_data: dict, lighthouse_data: dict):
    """
    Sends website audit data to GPT and returns analysis.
    """

    prompt = f"""
You are an expert website auditor.

Analyze this website audit data and provide insights.

Website URL:
{url}

Crawler Data:
{crawl_data}

Lighthouse Results:
{lighthouse_data}

Provide:

1. Overall health summary
2. SEO issues
3. Performance issues
4. Accessibility issues
5. Top 5 recommended fixes
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a professional website auditor."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content
