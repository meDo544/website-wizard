# app/dependencies/subscription.py

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.entitlement_service import EntitlementService


# -------------------------------
# 🔥 Feature-Based Guards (NEW)
# -------------------------------

def require_publish_permission(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    entitlements = EntitlementService(db)

    if not entitlements.can_publish(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Upgrade your plan to publish sites.",
        )

    return current_user


def require_custom_domain_permission(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    entitlements = EntitlementService(db)

    if not entitlements.can_use_custom_domain(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Upgrade your plan to use a custom domain.",
        )

    return current_user


def require_export_permission(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    entitlements = EntitlementService(db)

    if not entitlements.can_export(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Upgrade your plan to export your site.",
        )

    return current_user


# -------------------------------
# 🔥 Usage Limit Guard (UPDATED)
# -------------------------------

def require_site_creation_allowed(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    entitlements = EntitlementService(db)

    # 🔥 Count current sites
    from app.models.generated_site import GeneratedSite

    site_count = (
        db.query(GeneratedSite)
        .filter(GeneratedSite.user_id == current_user.id)
        .count()
    )

    if not entitlements.can_create_site(current_user.id, site_count):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Site limit reached. Upgrade your plan.",
        )

    return current_user


# -------------------------------
# 🔥 Generic Feature Gate (FLEXIBLE)
# -------------------------------

def require_feature(feature_name: str):
    """
    Dynamic feature gate.

    Example:
        Depends(require_feature("can_publish"))
    """

    def dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        entitlements = EntitlementService(db)
        features = entitlements.get_features(current_user.id)

        if not hasattr(features, feature_name):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Feature '{feature_name}' not defined.",
            )

        if not getattr(features, feature_name):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{feature_name} requires a higher plan.",
            )

        return current_user

    return dependency
