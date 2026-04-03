import time
import redis
import json

from backend.services.crawler import WebsiteCrawler
from backend.services.lighthouse_runner import run_lighthouse
from backend.services.gpt_analyzer import analyze_audit


r = redis.Redis(host="redis", port=6379, decode_responses=True)


def process_audit(data):

    url = data["url"]

    crawler = WebsiteCrawler()
    crawl_data = crawler.crawl(url)

    lighthouse_data = run_lighthouse(url)

    analysis = analyze_audit(url, crawl_data, lighthouse_data)

    result = {
        "url": url,
        "crawl": crawl_data,
        "lighthouse": lighthouse_data,
        "analysis": analysis
    }

    print("Audit completed:", result)


while True:

    job = r.blpop("audit_queue")

    if job:

        _, payload = job

        data = json.loads(payload)

        process_audit(data)