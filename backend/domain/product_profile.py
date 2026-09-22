from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProductItem:
    name: str
    description: str

    def to_dict(
        self,
    ) -> dict[str, str]:

        return {
            "name": self.name,
            "description": self.description,
        }


@dataclass
class ProductProfile:
    products: list[ProductItem] = field(
        default_factory=list
    )

    @classmethod
    def from_dict(
        cls,
        profile: dict[str, Any],
    ) -> "ProductProfile":

        products = profile.get(
            "products",
            [],
        )

        if not isinstance(
            products,
            list,
        ):
            return cls()

        normalized: list[ProductItem] = []

        for product in products:

            if not isinstance(
                product,
                dict,
            ):
                continue

            name = str(
                product.get(
                    "name",
                    "",
                )
            ).strip()

            description = str(
                product.get(
                    "description",
                    "",
                )
            ).strip()

            if name and description:

                normalized.append(
                    ProductItem(
                        name=name,
                        description=description,
                    )
                )

        return cls(
            products=normalized
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "products": [
                product.to_dict()
                for product in self.products
            ]
        }
