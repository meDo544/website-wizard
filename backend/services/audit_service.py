from backend.models.admin_audit import AdminAudit


class AuditService:
    """
    Service for recording admin/security audit events.
    """

    def __init__(self, db):
        self.db = db

    def log(
        self,
        user_id,
        action,
        entity_type=None,
        entity_id=None,
        metadata_json=None,
    ):
        """
        Create audit log entry.
        """

        audit = AdminAudit(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata_json=metadata_json,
        )

        self.db.add(audit)
        self.db.commit()

        return audit
