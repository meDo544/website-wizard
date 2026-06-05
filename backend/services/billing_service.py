# backend/services/billing_service.py

PRICE_TO_PLAN = {
    # 🔥 REPLACE with your real Stripe price IDs
    "price_123": "pro",
    "price_456": "team",
}


def get_plan_name_from_price(price_id: str) -> str | None:
    return PRICE_TO_PLAN.get(price_id)
