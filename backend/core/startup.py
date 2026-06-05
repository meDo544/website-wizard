import os

from sqlalchemy.orm import Session

from backend.models.plan import Plan
from backend.models.role import Role

from backend.models.plan_feature import (
    PlanFeature,
)

from backend.core.database import (
    SessionLocal,
)


# ---------------------------------------------------
# Validate Environment Variables
# ---------------------------------------------------

def validate_environment():
    required_vars = [
        "DATABASE_URL",
        "SECRET_KEY",
    ]

    missing = []

    for var in required_vars:

        if not os.getenv(var):
            missing.append(var)

    if missing:
        raise RuntimeError(
            f"Missing environment variables: {missing}"
        )

    print("✅ Environment validation passed")


# ---------------------------------------------------
# Ensure required roles exist
# ---------------------------------------------------

def ensure_roles(db: Session):

    required_roles = [
        "admin",
    ]

    for role_name in required_roles:

        existing = (
            db.query(Role)
            .filter(Role.name == role_name)
            .first()
        )

        if not existing:

            role = Role(
                name=role_name,
            )

            db.add(role)

    db.commit()

    print("✅ Role validation passed")


# ---------------------------------------------------
# Ensure plans exist
# ---------------------------------------------------

def ensure_plans(db: Session):

    required_plans = [
        "free",
        "pro",
        "team",
    ]

    for plan_name in required_plans:

        existing = (
            db.query(Plan)
            .filter(Plan.name == plan_name)
            .first()
        )

        if not existing:

            plan = Plan(
                name=plan_name,
                is_active=True,
            )

            db.add(plan)

    db.commit()

    print("✅ Plan validation passed")


# ---------------------------------------------------
# Ensure plan features exist
# ---------------------------------------------------

def ensure_plan_features(db: Session):

    plans = db.query(Plan).all()

    for plan in plans:

        existing = (
            db.query(PlanFeature)
            .filter(
                PlanFeature.plan_id == plan.id
            )
            .first()
        )

        if existing:
            continue

        # ---------------------------------
        # Free Plan
        # ---------------------------------

        if plan.name == "free":

            feature = PlanFeature(
                plan_id=plan.id,

                can_publish=False,

                can_use_custom_domain=False,

                can_export=False,

                max_sites=1,

                max_ai_credits=10,
            )

        # ---------------------------------
        # Pro Plan
        # ---------------------------------

        elif plan.name == "pro":

            feature = PlanFeature(
                plan_id=plan.id,

                can_publish=True,

                can_use_custom_domain=True,

                can_export=True,

                max_sites=10,

                max_ai_credits=100,
            )

        # ---------------------------------
        # Team Plan
        # ---------------------------------

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
            continue

        db.add(feature)

    db.commit()

    print("✅ Plan feature validation passed")


# ---------------------------------------------------
# Full startup bootstrap
# ---------------------------------------------------

def run_startup_checks():

    print("🚀 Running startup validation...")

    validate_environment()

    db = SessionLocal()

    try:

        ensure_roles(db)

        ensure_plans(db)

        ensure_plan_features(db)

        print(
            "✅ Startup validation completed"
        )

    finally:
        db.close()
