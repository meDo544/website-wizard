import time

from backend.core.celery_app import celery


@celery.task
def run_demo_audit(url: str):

    print(f"🚀 Starting audit for: {url}")

    # Simulate long-running task
    time.sleep(10)

    print(f"✅ Audit completed: {url}")

    return {
        "success": True,
        "url": url,
    }
