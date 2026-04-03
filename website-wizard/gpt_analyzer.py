import os
from openai import OpenAI

# Lazy client (safe for workers)
_client = None

def get_client():
    global _client
    if _client:
        return _client

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    _client = OpenAI(api_key=api_key)
    return _client


def analyze_website(url, crawl_data, lighthouse_result):
    client = get_client()

    prompt = f"""
You are Website Wizard. Analyze the following website data and return:
- 3 SEO issues
- 2 UX suggestions
- Code fix example

URL: {url}

Crawl Data:
{crawl_data}

Lighthouse:
{lighthouse_result}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # cheaper + faster for workers
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            timeout=30,  # critical for worker stability
        )

        return response.choices[0].message.content

    except Exception as e:
        # Never let GPT crash your worker
        return f"GPT_ANALYSIS_FAILED: {str(e)}"