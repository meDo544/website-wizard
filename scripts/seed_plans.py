# scripts/seed_plans.py

from backend.core.database import SessionLocal
from backend.models.plan import Plan


def seed_plans():
    db = SessionLocal()

    plans = [
        {"name": "free"},
        {"name": "pro"},
        {"name": "team"},
    ]

    for p in plans:
        existing = db.query(Plan).filter(Plan.name == p["name"]).first()
        if not existing:
            db.add(Plan(name=p["name"]))

    db.commit()
    db.close()
    print("✅ Plans seeded successfully")


if __name__ == "__main__":
    seed_plans()
