# backend/routes/audits.py

from __future__ import annotations

import asyncio
import json

from typing import Any, AsyncGenerator, Optional
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)

from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
)

from sqlalchemy.orm import Session

from sse_starlette import EventSourceResponse

from backend.core.database import get_db

from backend.dependencies.auth import (
    get_current_user,
)

from backend.models.audit import Audit
from backend.models.user import User

from backend.tasks.full_audit_task import (
    run_full_audit_task,
)


router = APIRouter(
    prefix="/audits",
    tags=["audits"],
)


# ---------------------------------------------------
# Constants
# ---------------------------------------------------

TERMINAL_AUDIT_STATUSES = {
    "completed",
    "failed",
}

STREAM_POLL_INTERVAL_SECONDS = 1


# ---------------------------------------------------
# Request Schemas
# ---------------------------------------------------

class AuditCreateRequest(BaseModel):
    """
    Request body for creating audits.
    """

    url: HttpUrl = Field(
        ...,
        description="Website URL to audit.",
    )


# ---------------------------------------------------
# Helpers
# ---------------------------------------------------

def serialize_datetime(
    value: Any,
) -> Optional[str]:
    """
    Safely serialize datetime values.
    """

    if value is None:
        return None

    if hasattr(value, "isoformat"):
        return value.isoformat()

    return str(value)


def get_owned_audit_or_404(
    *,
    db: Session,
    audit_id: str,
    current_user: User,
) -> Audit:
    """
    Retrieve audit belonging to current user.
    """

    try:

        parsed_audit_id = UUID(
            str(audit_id)
        )

    except ValueError:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid audit ID.",
        )

    audit = (
        db.query(Audit)
        .filter(
            Audit.id == parsed_audit_id,
            Audit.user_id == current_user.id,
        )
        .first()
    )

    if audit is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit not found.",
        )

    return audit


def serialize_audit_summary(
    audit: Audit,
) -> dict[str, Any]:
    """
    Lightweight audit serializer.
    """

    return {

        "audit_id": str(audit.id),

        "url": audit.url,

        "status": audit.status,

        "progress_percentage": (
            audit.progress_percentage or 0
        ),

        "current_step": (
            audit.current_step or audit.status
        ),

        "overall_score": (
            audit.overall_score
        ),

        "created_at": (
            serialize_datetime(
                audit.created_at
            )
        ),

        "updated_at": (
            serialize_datetime(
                getattr(
                    audit,
                    "updated_at",
                    None,
                )
            )
        ),

        "completed_at": (
            serialize_datetime(
                audit.completed_at
            )
        ),
    }


def serialize_audit_status(
    audit: Audit,
) -> dict[str, Any]:
    """
    Lightweight serializer optimized
    for frontend polling and SSE.
    """

    status_value = (
        audit.status or "queued"
    )

    return {

        "audit_id": str(audit.id),

        "url": audit.url,

        "status": status_value,

        "progress_percentage": (
            audit.progress_percentage or 0
        ),

        "current_step": (
            audit.current_step or status_value
        ),

        "is_terminal": (
            status_value
            in TERMINAL_AUDIT_STATUSES
        ),

        "created_at": (
            serialize_datetime(
                audit.created_at
            )
        ),

        "updated_at": (
            serialize_datetime(
                getattr(
                    audit,
                    "updated_at",
                    None,
                )
            )
        ),

        "started_at": (
            serialize_datetime(
                audit.started_at
            )
        ),

        "completed_at": (
            serialize_datetime(
                audit.completed_at
            )
        ),

        "error_message": (
            audit.error_message
            if status_value == "failed"
            else None
        ),
    }


def serialize_audit_detail(
    audit: Audit,
) -> dict[str, Any]:
    """
    Full audit serializer.
    """

    data = serialize_audit_status(
        audit
    )

    data.update({

        "overall_score": (
            audit.overall_score
        ),

        "performance_score": (
            audit.performance_score
        ),

        "seo_score": (
            audit.seo_score
        ),

        "accessibility_score": (
            audit.accessibility_score
        ),

        "best_practices_score": (
            audit.best_practices_score
        ),

        "crawl_data": (
            audit.crawl_data
        ),

        "lighthouse_data": (
            audit.lighthouse_data
        ),

        "gpt_report": (
            audit.gpt_report
        ),
    })

    return data


# ---------------------------------------------------
# Create Audit
# ---------------------------------------------------

@router.post(
    "/",
    status_code=status.HTTP_202_ACCEPTED,
)
def create_audit(
    payload: AuditCreateRequest,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db),
):
    """
    Create new website audit.
    """

    audit = Audit(

        user_id=current_user.id,

        url=str(payload.url),

        status="queued",

        progress_percentage=0,

        current_step="queued",
    )

    db.add(audit)

    db.commit()

    db.refresh(audit)

    try:

        celery_result = (
            run_full_audit_task.delay(
                str(audit.id)
            )
        )

    except Exception as exc:

        audit.status = "failed"

        audit.current_step = "failed"

        audit.error_message = (
            f"Failed to queue audit: {str(exc)}"
        )

        db.add(audit)

        db.commit()

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Failed to queue audit."
            ),
        )

    return {

        "success": True,

        "message": (
            "Audit queued successfully."
        ),

        "audit_id": str(audit.id),

        "task_id": str(celery_result.id),

        "status": audit.status,

        "progress_percentage": (
            audit.progress_percentage
        ),

        "current_step": (
            audit.current_step
        ),

        "polling_url": (
            f"/audits/{audit.id}/status"
        ),

        "stream_url": (
            f"/audits/{audit.id}/stream"
        ),
    }


# ---------------------------------------------------
# List User Audits
# ---------------------------------------------------

@router.get("/")
def list_audits(
    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db),
):
    """
    List audits for current user.
    """

    audits = (
        db.query(Audit)
        .filter(
            Audit.user_id == current_user.id
        )
        .order_by(
            Audit.created_at.desc()
        )
        .all()
    )

    return {

        "count": len(audits),

        "audits": [

            serialize_audit_summary(
                audit
            )

            for audit in audits
        ],
    }


# ---------------------------------------------------
# Audit Status Polling
# ---------------------------------------------------

@router.get("/{audit_id}/status")
def get_audit_status(
    audit_id: str,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db),
):
    """
    Lightweight polling endpoint.
    """

    audit = get_owned_audit_or_404(
        db=db,
        audit_id=audit_id,
        current_user=current_user,
    )

    return serialize_audit_status(
        audit
    )


# ---------------------------------------------------
# SSE Live Stream
# IMPORTANT:
# Must appear BEFORE /{audit_id}
# ---------------------------------------------------

@router.get("/{audit_id}/stream")
async def stream_audit_progress(
    request: Request,

    audit_id: str,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db),
):
    """
    Stream live audit progress updates.
    """

    get_owned_audit_or_404(
        db=db,
        audit_id=audit_id,
        current_user=current_user,
    )

    async def event_generator() -> AsyncGenerator:

        last_payload = None

        while True:

            # ---------------------------------
            # Client disconnected
            # ---------------------------------

            if await request.is_disconnected():

                break

            # ---------------------------------
            # Refresh SQLAlchemy state
            # ---------------------------------

            db.expire_all()

            audit = get_owned_audit_or_404(
                db=db,
                audit_id=audit_id,
                current_user=current_user,
            )

            payload = (
                serialize_audit_status(
                    audit
                )
            )

            payload_json = json.dumps(
                payload,
                default=str,
            )

            # ---------------------------------
            # Only emit changed states
            # ---------------------------------

            if payload_json != last_payload:

                yield {

                    "event": "audit_update",

                    "data": payload_json,
                }

                last_payload = payload_json

            # ---------------------------------
            # Terminal states
            # ---------------------------------

            if payload["is_terminal"]:

                yield {

                    "event": "audit_complete",

                    "data": payload_json,
                }

                break

            await asyncio.sleep(
                STREAM_POLL_INTERVAL_SECONDS
            )

    return EventSourceResponse(
        event_generator(),
        ping=15,
    )


# ---------------------------------------------------
# Get Single Audit Detail
# IMPORTANT:
# Must remain LAST dynamic route
# ---------------------------------------------------

@router.get("/{audit_id}")
def get_audit(
    audit_id: str,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db),
):
    """
    Retrieve full audit detail.
    """

    audit = get_owned_audit_or_404(
        db=db,
        audit_id=audit_id,
        current_user=current_user,
    )

    return serialize_audit_detail(
        audit
    )
