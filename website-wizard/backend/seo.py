from collections import Counter
import re

# -------------------------
# STOPWORDS
# -------------------------
STOPWORDS = {
    "the", "and", "is", "in", "to", "of", "for", "on", "with", "at", "by",
    "an", "be", "this", "that", "it", "as", "are", "from", "or"
}

# -------------------------
# KEYWORD EXTRACTION
# -------------------------
def extract_keywords(text: str, top_n: int = 10):
    words = re.findall(r"[a-zA-Z]{3,}", text.lower())
    words = [w for w in words if w not in STOPWORDS]
    return Counter(words).most_common(top_n)

# -------------------------
# SCORE → GRADE
# -------------------------
def score_to_grade(score: int) -> str:
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    return "F"

# -------------------------
# PRIORITY CLASSIFIER
# -------------------------
def classify_priority(issue: str) -> str:
    high = {
        "Missing <title> tag",
        "Missing meta description",
        "Thin content"
    }
    medium = {
        "Title length is not optimal",
        "No internal links found"
    }
    if issue in high:
        return "High"
    if issue in medium:
        return "Medium"
    return "Low"

# -------------------------
# FIX GENERATOR
# -------------------------
def generate_fix(issue: str) -> dict:
    fixes = {
        "Missing <title> tag": {
            "action": "Add a <title> tag",
            "example": "<title>Primary Keyword – Brand</title>",
            "why": "Title tags are the strongest on-page ranking factor."
        },
        "Title length is not optimal": {
            "action": "Adjust title length",
            "example": "<title>Primary Keyword | Secondary</title>",
            "why": "Optimal length avoids SERP truncation."
        },
        "Missing meta description": {
            "action": "Add meta description",
            "example": '<meta name="description" content="120–160 char summary">',
            "why": "Improves CTR from search results."
        },
        "Thin content": {
            "action": "Expand content",
            "example": "Add FAQs, guides, and detailed explanations.",
            "why": "Search engines reward comprehensive pages."
        },
        "No internal links found": {
            "action": "Add internal links",
            "example": '<a href="/services">Our Services</a>',
            "why": "Improves crawlability and authority flow."
        },
        "No external links found": {
            "action": "Add authoritative outbound links",
            "example": '<a href="https://example.com">Trusted source</a>',
            "why": "Helps establish topical relevance."
        }
    }

    return fixes.get(issue, {
        "action": "Manual review required",
        "example": "N/A",
        "why": "Custom SEO judgment needed."
    })

# -------------------------
# MAIN ANALYSIS
# -------------------------
def analyze_seo(audit: dict) -> dict:
    category_weights = {
        "on_page": 45,
        "content": 25,
        "links": 20,
        "technical": 10
    }

    seo = {
        "score": 0,
        "grade": "",
        "summary": "",
        "category_scores": {},
        "category_explanations": {},
        "issues": [],
        "keywords": []
    }

    # ---------- ON-PAGE ----------
    on_page = category_weights["on_page"]
    title = audit.get("title")
    meta = audit.get("meta_description")

    if not title:
        on_page -= 15
        issue = "Missing <title> tag"
        seo["issues"].append({
            "issue": issue,
            "priority": classify_priority(issue),
            "fix": generate_fix(issue)
        })
    elif len(title) < 30 or len(title) > 65:
        on_page -= 5
        issue = "Title length is not optimal"
        seo["issues"].append({
            "issue": issue,
            "priority": classify_priority(issue),
            "fix": generate_fix(issue)
        })

    if not meta:
        on_page -= 10
        issue = "Missing meta description"
        seo["issues"].append({
            "issue": issue,
            "priority": classify_priority(issue),
            "fix": generate_fix(issue)
        })

    seo["category_scores"]["on_page"] = max(on_page, 0)

    # ---------- CONTENT ----------
    content = category_weights["content"]
    text = audit.get("text", "")
    seo["keywords"] = extract_keywords(text)

    if len(text.split()) < 300:
        content -= 10
        issue = "Thin content"
        seo["issues"].append({
            "issue": issue,
            "priority": classify_priority(issue),
            "fix": generate_fix(issue)
        })

    seo["category_scores"]["content"] = max(content, 0)

    # ---------- LINKS ----------
    links = category_weights["links"]
    internal = audit.get("links", {}).get("internal", [])
    external = audit.get("links", {}).get("external", [])

    if not internal:
        links -= 10
        issue = "No internal links found"
        seo["issues"].append({
            "issue": issue,
            "priority": classify_priority(issue),
            "fix": generate_fix(issue)
        })

    if not external:
        links -= 5
        issue = "No external links found"
        seo["issues"].append({
            "issue": issue,
            "priority": classify_priority(issue),
            "fix": generate_fix(issue)
        })

    seo["category_scores"]["links"] = max(links, 0)

    # ---------- TECHNICAL ----------
    seo["category_scores"]["technical"] = category_weights["technical"]

    # ---------- FINAL ----------
    seo["score"] = sum(seo["category_scores"].values())
    seo["grade"] = score_to_grade(seo["score"])

    seo["category_explanations"] = {
        "on_page": "Titles, meta descriptions, and headings.",
        "content": "Depth, keywords, and quality.",
        "links": "Internal and external linking.",
        "technical": "Technical readiness."
    }

    seo["summary"] = f"Overall SEO grade: {seo['grade']}."

    return seo
