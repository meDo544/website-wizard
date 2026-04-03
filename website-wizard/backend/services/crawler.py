  from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

def crawl_website(url: str) -> dict:
    response = requests.get(url, timeout=20, headers={"User-Agent": "WebsiteWizardBot/1.0"})
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    title = soup.title.string.strip() if soup.title and soup.title.string else None
    meta_description = None
    meta_tag = soup.find("meta", attrs={"name": "description"})
    if meta_tag:
        meta_description = meta_tag.get("content")

    h1_tags = [h.get_text(strip=True) for h in soup.find_all("h1")]
    links = [a.get("href") for a in soup.find_all("a", href=True)]

    internal_links = []
    external_links = []
    domain = urlparse(url).netloc

    for link in links:
        absolute = urljoin(url, link)
        if urlparse(absolute).netloc == domain:
            internal_links.append(absolute)
        else:
            external_links.append(absolute)

    return {
        "final_url": response.url,
        "status_code": response.status_code,
        "title": title,
        "meta_description": meta_description,
        "h1_tags": h1_tags,
        "internal_links_count": len(set(internal_links)),
        "external_links_count": len(set(external_links)),
        "sample_internal_links": list(set(internal_links))[:20],
        "sample_external_links": list(set(external_links))[:20],
    }      