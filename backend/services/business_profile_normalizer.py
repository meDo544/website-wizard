from typing import Any


def normalize_generated_business_profile(
    profile: dict[str, Any],
) -> dict[str, Any]:
    if not profile.get("offer_variants"):
        profile["offer_variants"] = [
            {
                "type": "discount",
                "headline": "Special Offer Available Today",
            },
            {
                "type": "consultation",
                "headline": "Free Consultation Available",
            },
            {
                "type": "bonus",
                "headline": "Bonus Service Included",
            },
        ]

    branding = profile.get(
        "branding",
        {},
    )

    if not profile.get("trust_variants"):
        profile["trust_variants"] = [
            {
                "type": "reviews",
                "headline": "Trusted by Happy Customers",
            },
            {
                "type": "experience",
                "headline": "Experienced Professionals You Can Rely On",
            },
            {
                "type": "guarantee",
                "headline": "Satisfaction Guaranteed",
            },
        ]

    if not profile.get("social_proof_variants"):
        profile["social_proof_variants"] = [
            {
                "type": "customers",
                "headline": "Trusted by Customers",
            },
            {
                "type": "projects",
                "headline": "Successful Projects Delivered",
            },
            {
                "type": "community",
                "headline": "Join Our Growing Community",
            },
        ]

    if not profile.get("risk_reversal_variants"):
        profile["risk_reversal_variants"] = [
            {
                "type": "guarantee",
                "headline": "100% Satisfaction Guarantee",
            },
            {
                "type": "money_back",
                "headline": "30-Day Money Back Guarantee",
            },
            {
                "type": "free_trial",
                "headline": "Try It Risk Free",
            },
        ]

    if not profile.get("urgency_variants"):
        profile["urgency_variants"] = [
            {
                "type": "limited_time",
                "headline": "Offer Ends This Week",
            },
            {
                "type": "limited_spots",
                "headline": "Only 5 Spots Remaining",
            },
            {
                "type": "seasonal",
                "headline": "Seasonal Promotion Available",
            },
        ]

    if not profile.get("objection_variants"):
        profile["objection_variants"] = [
            {
                "type": "price",
                "headline": "Affordable Options Available",
            },
            {
                "type": "complexity",
                "headline": "Easy Setup and Ongoing Support",
            },
            {
                "type": "trust",
                "headline": "Trusted by Thousands of Customers",
            },
        ]

    if not profile.get("value_prop_variants"):
        profile["value_prop_variants"] = [
            {
                "type": "quality",
                "headline": "Premium Quality You Can Trust",
            },
            {
                "type": "speed",
                "headline": "Get Results Faster",
            },
            {
                "type": "cost_savings",
                "headline": "Save Time and Money",
            },
        ]

    if not profile.get("audience_variants"):
        profile["audience_variants"] = [
            {
                "type": "consumer",
                "headline": "Perfect for Everyday Customers",
            },
            {
                "type": "professional",
                "headline": "Built for Professionals",
            },
            {
                "type": "small_business",
                "headline": "Designed for Growing Businesses",
            },
         ]

    if not profile.get("differentiation_variants"):
        profile["differentiation_variants"] = [
            {
                "type": "quality",
                "headline": (
                    "Higher Quality Than Typical Alternatives"
                ),
            },
            {
                "type": "innovation",
                "headline": (
                    "Advanced Technology That Sets Us Apart"
                ),
            },
            {
                "type": "service",
                "headline": (
                    "Personalized Support Every Step of the Way"
                ),
            },
         ]

    if not profile.get("emotional_trigger_variants"):
        profile["emotional_trigger_variants"] = [
            {
                "type": "aspiration",
                "headline": (
                    "Achieve More With Less Effort"
                ),
            },
            {
                "type": "security",
                "headline": (
                    "Feel Confident in Every Purchase"
                ),
            },
            {
                "type": "status",
                "headline": (
                    "Stand Out With Premium Solutions"
                ),
            },
        ]

    if not profile.get("buyer_motivation_variants"):
        profile["buyer_motivation_variants"] = [
            {
                "type": "save_time",
                "headline": (
                    "Get More Done in Less Time"
                ),
            },
            {
                "type": "save_money",
                "headline": (
                    "Keep More Money in Your Pocket"
                ),
            },
            {
                "type": "growth",
                "headline": (
                    "Accelerate Your Personal and Business Growth"
                ),
            },
        ]

    if not profile.get("pain_point_variants"):
        profile["pain_point_variants"] = [
            {
                "type": "time",
                "headline": (
                    "Stop Wasting Time on Outdated Solutions"
                ),
            },
            {
                "type": "cost",
                "headline": (
                    "Reduce Unnecessary Expenses"
                ),
            },
            {
                "type": "risk",
                "headline": (
                    "Avoid Costly Mistakes"
                ),
            },
        ]

    if not profile.get("outcome_variants"):
        profile["outcome_variants"] = [
            {
                "type": "growth",
                "headline": (
                    "Accelerate Your Business Growth"
                ),
            },
            {
                "type": "efficiency",
                "headline": (
                    "Get More Done With Less Effort"
                ),
            },
            {
                "type": "confidence",
                "headline": (
                    "Make Decisions With Confidence"
                ),
            },
        ]

    if not profile.get("authority_variants"):
        profile["authority_variants"] = [
            {
                "type": "expertise",
                "headline": (
                    "Trusted Experts in Your Industry"
                ),
            },
            {
                "type": "results",
                "headline": (
                    "Proven Results Backed by Real Success Stories"
                ),
            },
            {
                "type": "innovation",
                "headline": (
                    "Leading the Industry Through Innovation"
                ),
            },
        ]

    if not profile.get(
        "industry_conversion_variants"
    ):
        profile[
            "industry_conversion_variants"
        ] = [
            {
                "type": "saas",
                "headline": (
                    "Built for Fast-Growing SaaS Companies"
                ),
            },
            {
                "type": "ecommerce",
                "headline": (
                    "Optimized for High-Converting Online Stores"
                ),
            },
            {
                "type": "agency",
                "headline": (
                    "Designed for Agencies Scaling Client Results"
                ),
            },
        ]

    if "logo_text\n" in branding:
        branding["logo_text"] = branding.pop(
            "logo_text\n"
        )

    profile["branding"] = branding

    return profile
