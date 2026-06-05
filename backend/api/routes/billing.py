# backend/api/routes/billing.py (or wherever your webhook lives)

from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
import stripe
import os

from backend.core.database import get_db
from backend.models.subscription import Subscription
from backend.models.plan import Plan
from backend.models.user import User
from backend.services.billing_service import get_plan_name_from_price

router = APIRouter()


@router.post("/billing/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except Exception as e:
        return {"error": str(e)}

    event_type = event["type"]

    # ---------------------------------------------------
    # 🔥 Handle subscription events
    # ---------------------------------------------------
    if event_type in [
        "customer.subscription.created",
        "customer.subscription.updated",
    ]:
        stripe_subscription = event["data"]["object"]

        stripe_subscription_id = stripe_subscription["id"]
        stripe_customer_id = stripe_subscription["customer"]
        stripe_status = stripe_subscription["status"]

        # 🔥 Extract Stripe price ID
        stripe_price_id = stripe_subscription["items"]["data"][0]["price"]["id"]

        # ---------------------------------------------------
        # 🔥 Map Stripe price → internal plan
        # ---------------------------------------------------
        plan_name = get_plan_name_from_price(stripe_price_id)

        if not plan_name:
            raise Exception(f"Unknown Stripe price ID: {stripe_price_id}")

        plan = db.query(Plan).filter(Plan.name == plan_name).first()

        if not plan:
            raise Exception(f"Plan not found: {plan_name}")

        # ---------------------------------------------------
        # 🔥 Find user via Stripe customer ID
        # ---------------------------------------------------
        user = (
            db.query(User)
            .filter(User.stripe_customer_id == stripe_customer_id)
            .first()
        )

        if not user:
            raise Exception(f"User not found for customer: {stripe_customer_id}")

        # ---------------------------------------------------
        # 🔥 Find or create subscription
        # ---------------------------------------------------
        subscription = (
            db.query(Subscription)
            .filter(
                Subscription.stripe_subscription_id == stripe_subscription_id
            )
            .first()
        )

        if not subscription:
            subscription = Subscription(
                user_id=user.id,
                stripe_customer_id=stripe_customer_id,
                stripe_subscription_id=stripe_subscription_id,
                status=stripe_status,
            )
            db.add(subscription)

        # ---------------------------------------------------
        # 🔥 Update subscription fields
        # ---------------------------------------------------
        subscription.stripe_price_id = stripe_price_id
        subscription.plan_id = plan.id
        subscription.status = stripe_status

        db.commit()
        db.refresh(subscription)

    # ---------------------------------------------------
    # 🔥 Handle cancellations
    # ---------------------------------------------------
    elif event_type == "customer.subscription.deleted":
        stripe_subscription = event["data"]["object"]

        subscription = (
            db.query(Subscription)
            .filter(
                Subscription.stripe_subscription_id == stripe_subscription["id"]
            )
            .first()
        )

        if subscription:
            subscription.status = "canceled"
            db.commit()

    return {"status": "success"}
