from datetime import datetime, timezone
import logging
import socket
import time

from sqlalchemy.orm import Session

from backend.core.database import SessionLocal
from backend.models.audit import Audit
from backend.queue.redis_queue import dequeue_audit, enqueue_audit
from backend.services.crawler import crawl_website
from backend.services.lighthouse_runner import run_lighthouse
from backend.services.gpt_analyzer import analyze_website

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [worker] %(message)s",
)

MAX_RETRIES = 3
WORKER_ID = socket.gethostname()


def utcnow():
    return datetime.now(timezone.utc)


def claim_audit(db: Session, audit_id: int) -> Audit | None:
    rows_updated = (
        db.query(Audit)
        .filter(Audit.id == audit_id, Audit.status == "queued")
        .update(
            {
                Audit.status: "processing",
                Audit.started_at: utcnow(),
                Audit.updated_at: utcnow(),
                Audit.error_message: None,
                Audit.claimed_by: WORKER_ID,
                Audit.heartbeat_at: utcnow(),
            },
            synchronize_session=False,
        )
    )
    db.commit()

    if rows_updated == 0:
        logger.info(f"Skip audit_id={audit_id}: already claimed or not queued")
        return None

    return db.query(Audit).filter(Audit.id == audit_id).first()


def heartbeat(db: Session, audit_id: int):
    db.query(Audit).filter(Audit.id == audit_id).update(
        {
            Audit.heartbeat_at: utcnow(),
            Audit.updated_at: utcnow(),
        },
        synchronize_session=False,
    )
    db.commit()


def mark_completed(
    db: Session,
    audit: Audit,
    crawl_data,
    lighthouse_result,
    gpt_report,
):
    performance_score = lighthouse_result.get("performance_score")
    seo_score = lighthouse_result.get("seo_score")
    accessibility_score = lighthouse_result.get("accessibility_score")
    best_practices_score = lighthouse_result.get("best_practices_score")

    score_values = [
        v
        for v in [
            performance_score,
            seo_score,
            accessibility_score,
            best_practices_score,
        ]
        if v is not None
    ]
    overall_score = int(sum(score_values) / len(score_values)) if score_values else None

    audit.crawl_data = crawl_data
    audit.lighthouse_data = lighthouse_result.get("raw")
    audit.gpt_report = gpt_report

    audit.performance_score = performance_score
    audit.seo_score = seo_score
    audit.accessibility_score = accessibility_score
    audit.best_practices_score = best_practices_score
    audit.overall_score = overall_score

    audit.status = "completed"
    audit.completed_at = utcnow()
    audit.updated_at = utcnow()
    audit.heartbeat_at = utcnow()
    audit.error_message = None

    db.commit()


def mark_failed(db: Session, audit_id: int, error: str):
    audit = db.query(Audit).filter(Audit.id == audit_id).first()
    if not audit:
        return

    next_retry_count = (audit.retry_count or 0) + 1

    audit.retry_count = next_retry_count
    audit.last_error_at = utcnow()
    audit.error_message = error[:2000]
    audit.updated_at = utcnow()
    audit.heartbeat_at = None
    audit.claimed_by = None

    if next_retry_count < MAX_RETRIES:
        audit.status = "queued"
        audit.completed_at = None
        db.commit()

        enqueue_audit({"audit_id": audit_id})
        logger.info(f"Requeued audit_id={audit_id} retry={next_retry_count}/{MAX_RETRIES}")
    else:
        audit.status = "failed"
        audit.completed_at = utcnow()
        db.commit()
        logger.error(f"Audit {audit_id} permanently failed after {next_retry_count} attempts")


def process_audit_job(audit_id: int):
    db: Session = SessionLocal()

    try:
        logger.info(f"Attempting claim audit_id={audit_id}")
        audit = claim_audit(db, audit_id)

        if not audit:
            return

        logger.info(f"Claimed audit_id={audit_id} worker={WORKER_ID}")

        heartbeat(db, audit_id)
        crawl_data = crawl_website(audit.url)

        heartbeat(db, audit_id)
        lighthouse_result = run_lighthouse(audit.url)

        heartbeat(db, audit_id)
        gpt_report = analyze_website(audit.url, crawl_data, lighthouse_result)

        heartbeat(db, audit_id)
        mark_completed(
            db=db,
            audit=audit,
            crawl_data=crawl_data,
            lighthouse_result=lighthouse_result,
            gpt_report=gpt_report,
        )
        logger.info(f"Audit {audit_id} completed successfully")

    except Exception as e:
        logger.exception(f"Audit {audit_id} failed")
        db.rollback()

        try:
            mark_failed(db, audit_id, str(e))
        except Exception:
            logger.exception(f"Failed to persist failure state for audit_id={audit_id}")

    finally:
        db.close()


def run_worker():
    logger.info(f"Worker started id={WORKER_ID}")

    while True:
        try:
            job = dequeue_audit(block=True, timeout=5)

            if not job:
                continue

            audit_id = job.get("audit_id")
            if not audit_id:
                logger.warning("Received job without audit_id")
                continue

            logger.info(f"Dequeued audit_id={audit_id}")
            process_audit_job(int(audit_id))

        except Exception:
            logger.exception("Worker loop error")
            time.sleep(2)


if __name__ == "__main__":
    run_worker()