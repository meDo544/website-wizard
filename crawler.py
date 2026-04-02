import requests


def crawl(url: str):
    try:
        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "WebsiteWizardBot/1.0"
            },
            verify=False
        )

        return {
            "success": True,
            "status_code": response.status_code,
            "content_length": len(response.text),
            "url": url
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "url": url
        }

if __name__ == "__main__":
    result = crawl("https://example.com")
    print(result)
