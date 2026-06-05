import os

import stripe


STRIPE_SECRET_KEY = os.getenv(
    "STRIPE_SECRET_KEY",
)

STRIPE_WEBHOOK_SECRET = os.getenv(
    "STRIPE_WEBHOOK_SECRET",
)

STRIPE_PRICE_ID_PRO = os.getenv(
    "STRIPE_PRICE_ID_PRO",
)

STRIPE_PRICE_ID_ENTERPRISE = os.getenv(
    "STRIPE_PRICE_ID_ENTERPRISE",
)

stripe.api_key = STRIPE_SECRET_KEY
