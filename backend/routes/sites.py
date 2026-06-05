from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.database import get_db

from backend.dependencies.auth import get_current_user

from backend.models.user import User
from backend.models.generated_site import GeneratedSite

from backend.services.entitlement_service import EntitlementService
from backend.services.usage_service import UsageService

from backend.utils.upgrade import upgrade_response
from backend.utils.warnings import build_usage_warning


router = APIRouter(
    prefix="/sites",
    tags=["sites"]
)


@router.post("/")
def create_site(
    payload: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a website for the current user.

    Includes:
    - plan enforcement
    - usage tracking
    - upgrade prompts
    - usage warnings
    """

    entitlements = EntitlementService(db)

    usage_service = UsageService(db)

    # ---------------------------------
    # Current usage + plan features
    # ---------------------------------

    usage = usage_service.get_or_create_usage(
        current_user.id
    )

    features = entitlements.get_features(
        current_user.id
    )

    # ---------------------------------
    # 🔥 Hard limit enforcement
    # ---------------------------------

    if usage.sites_created >= features.max_sites:

        return upgrade_response(
            message="You've reached your site limit.",
            current=usage.sites_created,
            limit=features.max_sites,
            recommended_plan="pro",
        )

    # ---------------------------------
    # 🔥 Pre-limit warning (80%)
    # ---------------------------------

    warning = build_usage_warning(
        current=usage.sites_created,
        limit=features.max_sites,
    )

    # ---------------------------------
    # Create site
    # ---------------------------------

    site = GeneratedSite(
        user_id=current_user.id,

        # Future fields:
        # title=payload.get("title"),
    )

    db.add(site)

    db.commit()

    db.refresh(site)

    # ---------------------------------
    # Track usage
    # ---------------------------------

    usage_service.increment_sites(
        current_user.id
    )

    # ---------------------------------
    # Success response
    # ---------------------------------

    return {
        "success": True,
        "message": "Site created successfully.",
        "site_id": str(site.id),

        # Optional usage warning
        "warning": warning,
    }
