from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.database import get_db

from backend.dependencies.admin import require_admin

from backend.models.user import User
from backend.models.subscription import Subscription
from backend.models.plan import Plan
from backend.models.usage import Usage

from backend.services.entitlement_service import EntitlementService
from backend.services.audit_service import AuditService


router = APIRouter(
    prefix="/admin/analytics",
    tags=["admin-analytics"]
)


# ---------------------------------------------------
# 🔹 Users Near Limits
# ---------------------------------------------------

@router.get("/usage")
def get_usage_analytics(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    usages = db.query(Usage).all()

    results = []

    entitlements = EntitlementService(db)

    for usage in usages:
        features = entitlements.get_features(usage.user_id)

        site_percent = 0
        ai_percent = 0

        if features.max_sites > 0:
            site_percent = (
                usage.sites_created / features.max_sites
            ) * 100

        if features.max_ai_credits > 0:
            ai_percent = (
                usage.ai_credits_used / features.max_ai_credits
            ) * 100

        results.append({
            "user_id": str(usage.user_id),

            "sites_created": usage.sites_created,
            "site_limit": features.max_sites,
            "site_usage_percent": round(site_percent),

            "ai_credits_used": usage.ai_credits_used,
            "ai_credit_limit": features.max_ai_credits,
            "ai_usage_percent": round(ai_percent),

            "near_site_limit": site_percent >= 80,
            "near_ai_limit": ai_percent >= 80,
        })

    # 🔥 Audit logging
    audit = AuditService(db)

    audit.log(
        user_id=current_user.id,
        action="view_usage_analytics",
        entity_type="analytics",
    )

    return {
        "users": results
    }


# ---------------------------------------------------
# 🔹 Plan Distribution
# ---------------------------------------------------

@router.get("/plans")
def get_plan_distribution(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    plans = db.query(Plan).all()

    results = []

    for plan in plans:
        subscription_count = (
            db.query(Subscription)
            .filter(
                Subscription.plan_id == plan.id,
                Subscription.status == "active",
            )
            .count()
        )

        results.append({
            "plan": plan.name,
            "active_subscriptions": subscription_count,
        })

    # 🔥 Audit logging
    audit = AuditService(db)

    audit.log(
        user_id=current_user.id,
        action="view_plan_distribution",
        entity_type="analytics",
    )

    return {
        "plans": results
    }


# ---------------------------------------------------
# 🔥 Revenue Signals
# ---------------------------------------------------

@router.get("/revenue-signals")
def get_revenue_signals(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    usages = db.query(Usage).all()

    entitlements = EntitlementService(db)

    upgrade_candidates = []

    for usage in usages:
        features = entitlements.get_features(usage.user_id)

        site_percent = 0

        if features.max_sites > 0:
            site_percent = (
                usage.sites_created / features.max_sites
            ) * 100

        if site_percent >= 80:
            upgrade_candidates.append({
                "user_id": str(usage.user_id),
                "usage_percent": round(site_percent),
                "recommended_action": "upgrade_prompt",
            })

    # 🔥 Audit logging
    audit = AuditService(db)

    audit.log(
        user_id=current_user.id,
        action="view_revenue_signals",
        entity_type="analytics",
    )

    return {
        "upgrade_candidates": upgrade_candidates
    }


# ---------------------------------------------------
# 🔹 Subscription Analytics
# ---------------------------------------------------

@router.get("/subscriptions")
def get_subscription_analytics(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    active = (
        db.query(Subscription)
        .filter(Subscription.status == "active")
        .count()
    )

    inactive = (
        db.query(Subscription)
        .filter(Subscription.status != "active")
        .count()
    )

    # 🔥 Audit logging
    audit = AuditService(db)

    audit.log(
        user_id=current_user.id,
        action="view_subscription_analytics",
        entity_type="analytics",
    )

    return {
        "active_subscriptions": active,
        "inactive_subscriptions": inactive,
    }


# ---------------------------------------------------
# 🔥 Full Analytics Dashboard
# ---------------------------------------------------

@router.get("/overview")
def get_admin_overview(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    total_users = db.query(User).count()

    active_subscriptions = (
        db.query(Subscription)
        .filter(Subscription.status == "active")
        .count()
    )

    total_usage_records = db.query(Usage).count()

    # 🔥 Audit logging
    audit = AuditService(db)

    audit.log(
        user_id=current_user.id,
        action="view_admin_overview",
        entity_type="analytics",
    )

    return {
        "total_users": total_users,
        "active_subscriptions": active_subscriptions,
        "usage_records": total_usage_records,
    }
