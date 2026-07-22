from dataclasses import dataclass, asdict
from typing import Any

@dataclass
class HeroProfile:
    hero_title: str = ""
    hero_subtitle: str = ""
    selected_hero_type: str = ""
    selected_hero: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "HeroProfile":
        return cls(
            hero_title=data.get("hero_title", ""),
            hero_subtitle=data.get("hero_subtitle", ""),
            selected_hero_type=data.get("selected_hero_type", ""),
            selected_hero=data.get("selected_hero"),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
