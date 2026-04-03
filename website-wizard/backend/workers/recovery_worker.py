import time
from datetime import datetime, timedelta, timezone

from backend.core.database import SessionLocal
from backend.models.audit import Audit

STALE_TIMEOUT_SECONDS = 120  # 2 minutes


def utcnow():
    return datetime.now(timezone.utc)


def recover_stuck_jobs():
    db = SessionLocal()

    try:
        cutoff = utcnow() - timedelta(seconds=STALE_TIMEOUT_SECONDS)

        stuck_jobs = (
            db.query(Audit)
            .filter(
                Audit.status == "processing",
                Audit.heartbeat_at < cutoff,
            )
            .all()
        )

        for job in stuck_jobs:
            print(f"Recovering stuck job {job.id}")

            job.status = "queued"
            job.claimed_by = None
            job.heartbeat_at = None
            job.updated_at = utcnow()

        db.commit()

    finally:
        db.close()


if __name__ == "__main__":
    while True:
        recover_stuck_jobs()
        time.sleep(30)