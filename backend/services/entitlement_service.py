# backend/services/entitlement_service.py

from sqlalchemy.orm import Session

from backend.models.subscription import Subscription
from backend.models.plan import Plan


class EntitlementService:
    def __init__(self, db: Session):
        self.db = db

    # -------------------------------
    # 🔹 Get user plan
    # -------------------------------
    def get_user_plan(self, user_id):
        subscription = (
            self.db.query(Subscription)
            .filter(Subscription.user_id == user_id)
            .order_by(Subscription.id.desc())
            .first()
        )

        if not subscription or subscription.status != "active":
            return self.db.query(Plan).filter(Plan.name == "free").first()

        return subscription.plan

    # -------------------------------
    # 🔹 Get features
    # -------------------------------
    def get_features(self, user_id):
        plan = self.get_user_plan(user_id)
        return plan.features

    # -------------------------------
    # 🔥 Feature checks
    # -------------------------------
    def can_publish(self, user_id):
        return self.get_features(user_id).can_publish

    def can_export(self, user_id):
        return self.get_features(user_id).can_export

    def can_use_custom_domain(self, user_id):
        return self.get_features(user_id).can_use_custom_domain

    # -------------------------------
    # 🔥 Usage limits
    # -------------------------------
    def can_create_site(self, user_id, current_site_count):
        features = self.get_features(user_id)
        return current_site_count < features.max_sites
