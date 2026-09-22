# backend/services/gpt_website_generator.py

from __future__ import annotations

import json
from typing import Any

import structlog

from backend.core.metrics import (
    record_gpt_tokens,
    track_gpt_duration,
)


from backend.services.business_profile_llm_client import (
    generate_business_profile_content,
    get_business_profile_model,
)
from backend.services.business_profile_prompt import (
    build_business_profile_system_prompt,
)
from backend.services.business_profile_telemetry import (
    log_business_profile_generation,
)
from backend.services.business_profile_normalizer import (
    normalize_generated_business_profile,
)
from backend.services.website_intelligence_pipeline import (
    run_website_intelligence_pipeline,
)


logger = structlog.get_logger(__name__)


def generate_business_profile(
    *,
    prompt: str,
    business_type: str,
    user_id: str = "system",
) -> dict[str, Any]:
    """
    Generate structured website content
    from a business description.
    """

    model = get_business_profile_model()

    logger.info(
        "Website generation started",
        business_type=business_type,
        model=model,
    )

    with track_gpt_duration(
        model=model,
        user_id=user_id,
    ) as metrics:

        try:

            system_prompt = build_business_profile_system_prompt()

            content, usage = (
                generate_business_profile_content(
                    system_prompt=system_prompt,
                    prompt=prompt,
                    business_type=business_type,
                    model=model,
                )
            )

            record_gpt_tokens(
                model=model,
                user_id=user_id,
                prompt_tokens=usage["prompt_tokens"],
                completion_tokens=usage["completion_tokens"],
                total_tokens=usage["total_tokens"],
            )


            profile = json.loads(content)

            profile = normalize_generated_business_profile(
                profile
            )


            profile = run_website_intelligence_pipeline(
                profile
            )

            metrics["status"] = "success"

            log_business_profile_generation(
                business_type=business_type,
                model=model,
                usage=usage,
                profile=profile,
            )

            profile["_usage"] = usage
            profile["_model"] = model

            return profile

        except Exception as exc:

            metrics["status"] = "failure"

            logger.exception(
                "Website generation failed",
                business_type=business_type,
                model=model,
                failure_type=exc.__class__.__name__,
            )

            raise
