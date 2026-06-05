from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import os
import stripe

from backend.core.dependencies import get_db
from backend.api.auth import get_current_user
from backend.models.user import User
from backend.models.subscription import Subscription

router = APIRouter(prefix="/billing", tags=["billing"])


# ---------------------------------------------------
# ENV CONFIG
# ---------------------------------------------------
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PRICE = os.getenv("STRIPE_PRICE_STARTER")
APP_URL = os.getenv("APP_BASE_URL", "http://localhost:8000")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")


# ---------------------------------------------------
# CHECKOUT
# ---------------------------------------------------
@router.post("/checkout")
def create_checkout(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Stripe API key not configured")

    if not STRIPE_PRICE:
        raise HTTPException(status_code=500, detail="Stripe price not configured")

    try:
        # Create Stripe customer
        customer = stripe.Customer.create(
            email=current_user.email,
        )

        # Create checkout session WITH metadata
        session = stripe.checkout.Session.create(
            mode="subscription",
            customer=customer.id,
            line_items=[
                {
                    "price": STRIPE_PRICE,
                    "quantity": 1,
                }
            ],
            success_url=f"{APP_URL}/?success=true",
            cancel_url=f"{APP_URL}/?cancel=true",
            metadata={
                "user_id": str(current_user.id)
            },
        )

        return {"url": session.url}

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=500, detail=f"Stripe error: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Checkout failed: {str(e)}")


# ---------------------------------------------------
# STRIPE WEBHOOK
# ---------------------------------------------------
@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="Webhook secret not configured")

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=STRIPE_WEBHOOK_SECRET,
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid webhook signature")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid webhook payload")

    event_type = event["type"]
    data = event["data"]["object"]

    # ---------------------------------------------------
    # HANDLE EVENTS
    # ---------------------------------------------------
    try:
        if event_type == "checkout.session.completed":
            print("✅ Checkout completed:", data.id)

            customer_id = data.customer
            subscription_id = data.subscription

            # SAFE METADATA ACCESS
            user_id = None
            if hasattr(data, "metadata") and data.metadata:
                try:
                    user_id = data.metadata.get("user_id")
                except Exception:
                    user_id = getattr(data.metadata, "user_id", None)

            if not user_id:
                print("⚠️ No user_id in metadata — skipping")
                return {"status": "skipped"}

            # ✅ KEEP UUID AS STRING (FINAL FIX)
            user_id = str(user_id)

            # Find user
            user = db.query(User).filter(User.id == user_id).first()

            if not user:
                print("⚠️ User not found:", user_id)
                return {"status": "skipped"}

            # Avoid duplicates
            existing = db.query(Subscription).filter(
                Subscription.stripe_subscription_id == subscription_id
            ).first()

            if not existing:
                sub = Subscription(
                    user_id=user.id,
                    stripe_customer_id=customer_id,
                    stripe_subscription_id=subscription_id,
                    status="active",
                )

                db.add(sub)
                db.commit()

                print("💰 Subscription saved for user:", user.id)
            else:
                print("ℹ️ Subscription already exists")

        elif event_type == "customer.subscription.updated":
            print("🔄 Subscription updated:", data.id)

            sub = db.query(Subscription).filter(
                Subscription.stripe_subscription_id == data.id
            ).first()

            if sub:
                sub.status = data.status
                db.commit()

        elif event_type == "customer.subscription.deleted":
            print("❌ Subscription canceled:", data.id)

            sub = db.query(Subscription).filter(
                Subscription.stripe_subscription_id == data.id
            ).first()

            if sub:
                sub.status = "canceled"
                db.commit()

        else:
            print("ℹ️ Unhandled event:", event_type)

    except Exception as e:
        print("⚠️ Webhook processing error:", str(e))

    return {"status": "success"}
