# scripts/bootstrap.py

"""
System bootstrap script for Website Wizard.

This script ensures all critical SaaS system data exists.

Includes:
- roles
- plans
- plan features
- default permissions (future-ready)

Run with:

    python -m scripts.bootstrap
"""

from backend.core.database import SessionLocal

from backend.models.role import Role
from backend.models.plan import Plan
from backend.models.plan_feature import (
    PlanFeature,
)


# ---------------------------------------------------
# Seed Roles
# ---------------------------------------------------

def seed_roles(db):

    roles = [
        "admin",
    ]

    for role_name in roles:

        existing = (
            db.query(Role)
            .filter(Role.name == role_name)
            .first()
        )

        if existing:
            continue

        role = Role(
            name=role_name,
        )

        db.add(role)

    db.commit()

    print("✅ Roles seeded")


# ---------------------------------------------------
# Seed Plans
# ---------------------------------------------------

def seed_plans(db):

    plans = [
        "free",
        "pro",
        "team",
    ]

    for plan_name in plans:

        existing = (
            db.query(Plan)
            .filter(Plan.name == plan_name)
            .first()
        )

        if existing:
            continue

        plan = Plan(
            name=plan_name,
            is_active=True,
        )

        db.add(plan)

    db.commit()

    print("✅ Plans seeded")


# ---------------------------------------------------
# Seed Plan Features
# ---------------------------------------------------

def seed_plan_features(db):

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
        # Free
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
        # Pro
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
        # Team
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

    print("✅ Plan features seeded")


# ---------------------------------------------------
# Full Bootstrap
# ---------------------------------------------------

def bootstrap():

    print("🚀 Running system bootstrap...")

    db = SessionLocal()

    try:

        seed_roles(db)

        seed_plans(db)

        seed_plan_features(db)

        print(
            "✅ System bootstrap completed"
        )

    finally:
        db.close()


# ---------------------------------------------------
# Entry Point
# ---------------------------------------------------

if __name__ == "__main__":
    bootstrap()
