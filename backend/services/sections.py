from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from enum import Enum

class ConversionRole(
    str,
    Enum,
):

    HERO = "hero"

    OFFER = "offer"

    TRUST = "trust"

    EDUCATION = "education"

    OBJECTION = "objection"

    CONTACT = "contact"

    ACTION = "action"

    OTHER = "other"

@dataclass(slots=True)
class Section:

    name: str

    html: str

    title: str = ""

    priority: int = 100

    visible: bool = True

    conversion_role: ConversionRole = (
        ConversionRole.OTHER
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


