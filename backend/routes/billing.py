import os
import stripe

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from backend.core.database import get_db

from backend.dependencies.auth import get_current_user

from backend.models.user import User
from backend.models.subscription import Subscription

from backend.services.entitlement_service import EntitlementService
from backend.services.usage_service import UsageService

from pydantic import BaseModel

class CheckoutRequest(BaseModel):

    plan: str

WEBHOOK_SECRET = os.getenv(
    "STRIPE_WEBHOOK_SECRET"
)

# ---------------------------------------------------
# Stripe Configuration
# ---------------------------------------------------

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


router = APIRouter(
    prefix="/billing",
    tags=["billing"]
)


# ---------------------------------------------------
# Environment Variables
# ---------------------------------------------------

STRIPE_PRICE_IDS = {
    "starter": os.getenv(
        "STRIPE_PRICE_ID_STARTER"
    ),

    "pro": os.getenv(
        "STRIPE_PRICE_ID_PRO"
    ),

    "enterprise": os.getenv(
        "STRIPE_PRICE_ID_ENTERPRISE"
    ),
}

SUCCESS_URL = os.getenv(
    "STRIPE_SUCCESS_URL"
)

CANCEL_URL = os.getenv(
    "STRIPE_CANCEL_URL"
)


# ---------------------------------------------------
# 🔹 Current Plan
# ---------------------------------------------------

@router.get("/plan")
def get_current_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    entitlements = EntitlementService(db)

    plan = entitlements.get_user_plan(current_user.id)

    return {
        "plan": plan.name,
    }


# ---------------------------------------------------
# 🔹 Current Usage
# ---------------------------------------------------

@router.get("/usage")
def get_usage(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    usage_service = UsageService(db)

    usage = usage_service.get_or_create_usage(
        current_user.id
    )

    return {
        "sites_created": usage.sites_created,
        "ai_credits_used": usage.ai_credits_used,
    }


# ---------------------------------------------------
# 🔹 Plan Limits
# ---------------------------------------------------

@router.get("/limits")
def get_limits(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    entitlements = EntitlementService(db)

    features = entitlements.get_features(
        current_user.id
    )

    return {
        "max_sites": features.max_sites,
        "max_ai_credits": features.max_ai_credits,
        "can_publish": features.can_publish,
        "can_export": features.can_export,
        "can_use_custom_domain": (
            features.can_use_custom_domain
        ),
    }


# ---------------------------------------------------
# 🔹 Full Billing Dashboard
# ---------------------------------------------------

@router.get("/dashboard")
def get_billing_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    entitlements = EntitlementService(db)

    usage_service = UsageService(db)

    plan = entitlements.get_user_plan(
        current_user.id
    )

    features = entitlements.get_features(
        current_user.id
    )

    usage = usage_service.get_or_create_usage(
        current_user.id
    )

    return {
        "plan": {
            "name": plan.name,
        },

        "usage": {
            "sites_created": usage.sites_created,
            "ai_credits_used": usage.ai_credits_used,
        },

        "limits": {
            "max_sites": features.max_sites,
            "max_ai_credits": features.max_ai_credits,
        },

        "features": {
            "can_publish": features.can_publish,
            "can_export": features.can_export,
            "can_use_custom_domain": (
                features.can_use_custom_domain
            ),
        },
    }


# ---------------------------------------------------
# 🔥 Upgrade Recommendations
# ---------------------------------------------------

@router.get("/recommendation")
def get_upgrade_recommendation(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    entitlements = EntitlementService(db)

    usage_service = UsageService(db)

    plan = entitlements.get_user_plan(
        current_user.id
    )

    features = entitlements.get_features(
        current_user.id
    )

    usage = usage_service.get_or_create_usage(
        current_user.id
    )

    recommendations = []

    # ---------------------------------
    # Sites usage warnings
    # ---------------------------------

    if usage.sites_created >= (
        features.max_sites * 0.8
    ):
        recommendations.append(
            "You're nearing your site limit. "
            "Upgrade for more capacity."
        )

    # ---------------------------------
    # AI credit usage warnings
    # ---------------------------------

    if usage.ai_credits_used >= (
        features.max_ai_credits * 0.8
    ):
        recommendations.append(
            "You're nearing your AI credit limit."
        )

    return {
        "current_plan": plan.name,

        "recommendations": recommendations,

        "upgrade_recommended": (
            len(recommendations) > 0
        ),
    }


# ---------------------------------------------------
# 🔥 Stripe Customer Portal
# ---------------------------------------------------

@router.post("/customer-portal")
def create_customer_portal(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Creates a Stripe Billing Portal session.

    Users can:
    - manage subscriptions
    - update payment methods
    - cancel subscriptions
    - view invoices
    """

    # ---------------------------------
    # Find subscription
    # ---------------------------------

    subscription = (
        db.query(Subscription)
        .filter(
            Subscription.user_id == current_user.id
        )
        .first()
    )

    if not subscription:
        raise HTTPException(
            status_code=404,
            detail="No subscription found.",
        )

    if not subscription.stripe_customer_id:
        raise HTTPException(
            status_code=400,
            detail="Stripe customer ID missing.",
        )

    # ---------------------------------
    # Create Stripe Billing Portal
    # ---------------------------------

    try:
        session = stripe.billing_portal.Session.create(
            customer=subscription.stripe_customer_id,

            # ⚠️ Replace in production
            return_url=(
                "http://34.27.91.3:3001/settings/billing"
            ),
        )

        return {
            "url": session.url
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ---------------------------------------------------
# 🔥 Stripe Checkout Session
# ---------------------------------------------------

@router.post("/create-checkout-session")
def create_checkout_session(
    payload: CheckoutRequest,
    current_user: User = Depends(
        get_current_user
    ),
):

    plan = payload.plan.lower()

    if plan not in STRIPE_PRICE_IDS:

        raise HTTPException(
            status_code=400,
            detail="Invalid plan selected.",
        )

    price_id = STRIPE_PRICE_IDS[plan]

    if not price_id:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Stripe price ID missing "
                f"for plan: {plan}"
            ),
        )

    try:

        session = stripe.checkout.Session.create(

            payment_method_types=["card"],

            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],

            mode="subscription",

            success_url=SUCCESS_URL,
            cancel_url=CANCEL_URL,

            customer_email=current_user.email,
        )

        return {
            "checkout_url": session.url
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

# ---------------------------------------------------
# Stripe Webhook
# ---------------------------------------------------

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
            payload=payload,
            sig_header=sig_header,
            secret=WEBHOOK_SECRET,
        )

    except stripe.error.SignatureVerificationError:

        raise HTTPException(
            status_code=400,
            detail="Invalid Stripe signature",
        )

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    # ---------------------------------------------------
    # Checkout Completed
    # ---------------------------------------------------

    if event["type"] == "checkout.session.completed":

        session = event["data"]["object"]

        customer_email = session.customer_email

        # Fallback to customer_details.email
        if not customer_email:

            if not customer_email and session.customer_details:

                       customer_email = (
                           session.customer_details.email
                       )

        print(
            f"Stripe customer email: "
            f"{customer_email}"
        )

        if customer_email:

            user = (
                db.query(User)
                .filter(
                    User.email == customer_email
                )
                .first()
            )

            if user:

                user.subscription_tier = (
                    "enterprise"
                )

                user.subscription_status = (
                    "active"
                )

                user.monthly_token_quota = (
                    5000000
                )

                user.monthly_spend_quota_usd = (
                    500.0
                )

                db.commit()

                print(
                    f"✅ Upgraded user: "
                    f"{user.email}"
                )

            else:

                print(
                    f"❌ User not found for "
                    f"{customer_email}"
                )

        else:

            print(
                "❌ No customer email found"
            )

    return {
        "status": "success"
    }

