from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class WebsiteCreate(BaseModel):
    project_name: str
    business_type: str
    prompt: str


class WebsiteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: Optional[UUID] = None
    project_name: Optional[str] = None
    business_type: Optional[str] = None
    prompt: str
    html: Optional[str] = None
    css: Optional[str] = None
    js: Optional[str] = None
    generated_url: Optional[str] = None
    generation_status: str
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
