"""
Stripe Billing Routes
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from jose import jwt
from sqlalchemy.orm import Session
import stripe

from backend.auth import oauth2_scheme
from backend.core.security import SECRET_KEY, ALGORITHM
from backend.core.database import get_db
from backend.core.stripe_config import (
    STRIPE_PRICE_ID_PRO,
    STRIPE_WEBHOOK_SECRET,
)
from backend.models.user import User
from backend.models.stripe_webhook_event import (
    StripeWebhookEvent,
)
from backend.services.subscription_service import SubscriptionService


router = APIRouter(
    prefix="/stripe",
    tags=["Stripe"],
)


def stripe_value(obj, key, default=None):
    """
    Safely access StripeObject values.
    """
    try:
        return obj[key]
    except Exception:
        return getattr(obj, key, default)


@router.post("/create-checkout-session")
def create_checkout_session(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token",
            )

        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found",
            )

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="subscription",
            customer=(
                user.stripe_customer_id
                if user.stripe_customer_id
                else None
            ),
            customer_email=(
                None
                if user.stripe_customer_id
                else user.email
            ),
            line_items=[
                {
                    "price": STRIPE_PRICE_ID_PRO,
                    "quantity": 1,
                }
            ],
            success_url="http://34.27.91.3:8000/health",
            cancel_url="http://34.27.91.3:8000/docs",
            metadata={
                "user_id": str(user.id),
                "email": user.email,
            },
            subscription_data={
                "metadata": {
                    "user_id": str(user.id),
                    "email": user.email,
                }
            },
        )

        return {
            "checkout_url": checkout_session.url
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    payload = await request.body()

    sig_header = request.headers.get(
        "stripe-signature"
    )

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            STRIPE_WEBHOOK_SECRET,
        )

    except Exception as exc:

        raise HTTPException(
            status_code=400,
            detail=f"Invalid webhook: {str(exc)}",
        )

    # ---------------------------------------------------
    # Stripe Event Metadata
    # ---------------------------------------------------

    event_id = event["id"]
    event_type = event["type"]

    # ---------------------------------------------------
    # Prevent Duplicate Processing
    # ---------------------------------------------------

    existing_event = (
        db.query(StripeWebhookEvent)
        .filter(
            StripeWebhookEvent.id == event_id
        )
        .first()
    )

    if existing_event:

        return {
            "status": "already_processed",
            "event_id": event_id,
        }

    # ---------------------------------------------------
    # Create Audit Record
    # ---------------------------------------------------

    webhook_event = StripeWebhookEvent(
        id=event_id,
        event_type=event_type,
        status="processing",
    )

    db.add(webhook_event)
    db.commit()

    print("WEBHOOK EVENT SAVED")
    print(webhook_event.id)

    saved_event = (
        db.query(StripeWebhookEvent)
        .filter(
            StripeWebhookEvent.id == event_id
        )
        .first()
    )

    print("DB LOOKUP RESULT:")
    print(saved_event)

    # ---------------------------------------------------
    # Process Webhook
    # ---------------------------------------------------

    try:

        # ---------------------------------------------------
        # CHECKOUT SESSION COMPLETED
        # ---------------------------------------------------

        if (
            event_type
            == "checkout.session.completed"
        ):

            session = event["data"]["object"]

            stripe_customer_id = stripe_value(
                session,
                "customer",
            )

            stripe_subscription_id = stripe_value(
                session,
                "subscription",
            )

            metadata = stripe_value(
                session,
                "metadata",
                {},
            )

            if metadata is None:
                metadata = {}

            try:
                user_id = metadata["user_id"]

            except Exception:
                user_id = None

            customer_email = stripe_value(
                session,
                "customer_email",
            )

            user = None

            # ---------------------------------------------------
            # Find User
            # ---------------------------------------------------

            if user_id:

                user = (
                    db.query(User)
                    .filter(User.id == user_id)
                    .first()
                )

            if (
                not user
                and customer_email
            ):

                user = (
                    db.query(User)
                    .filter(
                        User.email == customer_email
                    )
                    .first()
                )

            if not user:

                raise Exception(
                    "User not found for checkout session"
                )

            # ---------------------------------------------------
            # Persist Stripe IDs
            # ---------------------------------------------------

            user.stripe_customer_id = (
                stripe_customer_id
            )

            if hasattr(
                user,
                "stripe_subscription_id",
            ):

                user.stripe_subscription_id = (
                    stripe_subscription_id
                )

            # ---------------------------------------------------
            # Upgrade Subscription
            # ---------------------------------------------------

            user.subscription_tier = "pro"

            subscription_service = (
                SubscriptionService(db)
            )

            subscription_service.apply_subscription_tier(
                user
            )

        # ---------------------------------------------------
        # SUBSCRIPTION CANCELLED
        # ---------------------------------------------------

        elif (
            event_type
            == "customer.subscription.deleted"
        ):

            subscription = event["data"]["object"]

            stripe_customer_id = stripe_value(
                subscription,
                "customer",
            )

            user = (
                db.query(User)
                .filter(
                    User.stripe_customer_id
                    == stripe_customer_id
                )
                .first()
            )

            if user:

                user.subscription_tier = "free"

                subscription_service = (
                    SubscriptionService(db)
                )

                subscription_service.apply_subscription_tier(
                    user
                )

                db.commit()

        # ---------------------------------------------------
        # PAYMENT FAILED
        # ---------------------------------------------------

        elif (
            event_type
            == "invoice.payment_failed"
        ):

            invoice = event["data"]["object"]

            stripe_customer_id = stripe_value(
                invoice,
                "customer",
            )

            user = (
                db.query(User)
                .filter(
                    User.stripe_customer_id
                    == stripe_customer_id
                )
                .first()
            )

            if user:

                user.subscription_tier = (
                    "past_due"
                )

                db.commit()

        # ---------------------------------------------------
        # Mark Success
        # ---------------------------------------------------

        webhook_event.status = "processed"

        db.commit()

        return {
            "status": "success",
            "event_id": event_id,
        }

    except Exception as exc:

        db.rollback()

        webhook_event = (
            db.query(StripeWebhookEvent)
            .filter(
                StripeWebhookEvent.id == event_id
            )
            .first()
        )

        if webhook_event:

            webhook_event.status = "failed"

            webhook_event.error_message = (
                str(exc)
            )

            db.commit()

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )
