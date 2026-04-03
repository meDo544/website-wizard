from bs4 import BeautifulSoup
from urllib.parse import urlparse


def parse_html(html: str, base_url: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    # -----------------
    # Title
    # -----------------
    title = soup.title.string.strip() if soup.title and soup.title.string else None

    # -----------------
    # Meta description
    # -----------------
    meta_desc = None
    desc_tag = soup.find("meta", attrs={"name": "description"})
    if desc_tag and desc_tag.get("content"):
        meta_desc = desc_tag["content"].strip()

    # -----------------
    # Headings (H1–H6)
    # -----------------
    headings = {}
    for level in range(1, 7):
        tag = f"h{level}"
        headings[tag] = [h.get_text(strip=True) for h in soup.find_all(tag)]

    # -----------------
    # Links
    # -----------------
    parsed_base = urlparse(base_url)
    internal_links = []
    external_links = []

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()

        if href.startswith("/"):
            internal_links.append(base_url.rstrip("/") + href)

        elif href.startswith("http"):
            if parsed_base.netloc in href:
                internal_links.append(href)
            else:
                external_links.append(href)

    # -----------------
    # Visible text content (for keyword analysis)
    # -----------------
    text_content = soup.get_text(separator=" ", strip=True)

    # -----------------
    # Final structured return
    # -----------------
    return {
        "title": title,
        "meta_description": meta_desc,
        "headings": headings,
        "links": {
            "internal": list(set(internal_links)),
            "external": list(set(external_links)),
        },
        "text": text_content
    }
