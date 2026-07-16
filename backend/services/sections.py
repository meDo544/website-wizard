from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Section:

    name: str

    html: str

    title: str = ""

    priority: int = 100

    visible: bool = True

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


