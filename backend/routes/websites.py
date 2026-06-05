from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.models.generated_sites import GeneratedSite
from backend.models.user import User
from backend.schemas.website import WebsiteCreate, WebsiteResponse
from backend.dependencies.auth import get_current_user
from backend.tasks.website_generation import generate_website_task


router = APIRouter(
    prefix="/websites",
    tags=["websites"],
)


@router.post("/generate")
async def generate_website(
    website_data: WebsiteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    website = GeneratedSite(
        user_id=current_user.id,
        project_name=website_data.project_name,
        business_type=website_data.business_type,
        prompt=website_data.prompt,
        generation_status="queued",
    )

    db.add(website)
    db.commit()
    db.refresh(website)

    generate_website_task.delay(
        str(website.id),
        website.business_type,
    )

    return {
        "message": "Generation started",
        "website_id": str(website.id),
        "status": website.generation_status,
    }


@router.get(
    "/{website_id}",
    response_model=WebsiteResponse,
)
async def get_website_status(
    website_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    website = (
        db.query(GeneratedSite)
        .filter(
            GeneratedSite.id == website_id,
            GeneratedSite.user_id == current_user.id,
        )
        .first()
    )

    if not website:
        raise HTTPException(
            status_code=404,
            detail="Website not found",
        )

    return website


@router.get(
    "",
    response_model=list[WebsiteResponse],
)
async def list_websites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    websites = (
        db.query(GeneratedSite)
        .filter(
            GeneratedSite.user_id == current_user.id
        )
        .order_by(
            GeneratedSite.created_at.desc()
        )
        .all()
    )

    return websites

