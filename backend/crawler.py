import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


def crawl(url: str):
    """
    Crawl a website homepage and extract internal links.
    """

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    headers = {
        "User-Agent": "Mozilla/5.0 (WebsiteWizardBot/1.0)"
    }

    pages = []
    visited = set()

    try:

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        base_domain = urlparse(url).netloc

        pages.append(url)
        visited.add(url)

        for link in soup.find_all("a", href=True):

            href = link["href"]
            full_url = urljoin(url, href)

            if urlparse(full_url).netloc == base_domain:
                if full_url not in visited:
                    visited.add(full_url)
                    pages.append(full_url)

        return {
            "url": url,
            "pages_found": len(pages),
            "pages": pages[:50]  # prevent huge payloads
        }

    except Exception as e:

        return {
            "url": url,
            "error": str(e),
            "pages": []
        }
