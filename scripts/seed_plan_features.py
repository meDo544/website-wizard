# scripts/seed_plan_features.py

from backend.core.database import SessionLocal

# 🔥 REQUIRED: Import ALL models so SQLAlchemy registers relationships
from backend.models.plan import Plan
from backend.models.plan_feature import PlanFeature
from backend.models.subscription import Subscription
from backend.models.user import User


def seed_plan_features():
    db = SessionLocal()

    try:
        plans = db.query(Plan).all()

        for plan in plans:
            existing = db.query(PlanFeature).filter(
                PlanFeature.plan_id == plan.id
            ).first()

            if existing:
                continue

            if plan.name == "free":
                feature = PlanFeature(
                    plan_id=plan.id,
                    can_publish=False,
                    can_use_custom_domain=False,
                    can_export=False,
                    max_sites=1,
                    max_ai_credits=10,
                )

            elif plan.name == "pro":
                feature = PlanFeature(
                    plan_id=plan.id,
                    can_publish=True,
                    can_use_custom_domain=True,
                    can_export=True,
                    max_sites=10,
                    max_ai_credits=100,
                )

            elif plan.name == "team":
                feature = PlanFeature(
                    plan_id=plan.id,
                    can_publish=True,
                    can_use_custom_domain=True,
                    can_export=True,
                    max_sites=50,
                    max_ai_credits=500,
                )

            else:
                continue  # safety for unknown plans

            db.add(feature)

        db.commit()
        print("✅ Plan features seeded successfully")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding plan features: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    seed_plan_features()
