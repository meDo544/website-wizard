from backend.celery_app import celery_app

from backend.core.database import SessionLocal
from backend.models.user import User


def reset_monthly_quotas() -> None:
    """
    Reset monthly AI usage counters.
    """

    db = SessionLocal()

    try:

        users = db.query(User).all()

        for user in users:

            user.monthly_tokens_used = 0

            user.monthly_spend_used_usd = 0.0

            user.monthly_request_count = 0

        db.commit()

        print("✅ Monthly AI quotas reset.")

    finally:

        db.close()


@celery_app.task(
    name="backend.tasks.quota_reset.reset_monthly_quotas_task"
)
def reset_monthly_quotas_task():

    reset_monthly_quotas()
