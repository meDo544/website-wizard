# backend/services/gpt_analyzer.py

"""
GPT analyzer service.

Provides production-grade GPT observability:
- Request count
- Request latency
- Active requests
- Token telemetry
- Stable model labels
- Structured logs with audit correlation

Audit IDs and URLs are logged for debugging but never used as Prometheus labels.
"""

from __future__ import annotations

from typing import Any

import structlog
from openai import OpenAI

from backend.core.config import settings
from backend.core.metrics import record_gpt_tokens, track_gpt_duration

logger = structlog.get_logger(__name__)

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def _get_openai_model() -> str:
    """Return configured OpenAI model with safe fallback."""
    return getattr(settings, "OPENAI_MODEL", "gpt-4o-mini")


def _extract_usage(response: Any) -> dict[str, int]:
    """Extract token usage from OpenAI response safely."""
    usage = getattr(response, "usage", None)

    if usage is None:
        return {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        }

    return {
        "prompt_tokens": int(getattr(usage, "prompt_tokens", 0) or 0),
        "completion_tokens": int(getattr(usage, "completion_tokens", 0) or 0),
        "total_tokens": int(getattr(usage, "total_tokens", 0) or 0),
    }


def analyze_with_gpt(
    *,
    audit_id: str,
    url: str,
    lighthouse_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Analyze Lighthouse output using GPT.

    Args:
        audit_id: Audit identifier.
        url: Audited website URL.
        lighthouse_result: Parsed Lighthouse JSON result.

    Returns:
        Structured GPT analysis payload.
    """
    model = _get_openai_model()

    logger.info(
        "GPT analysis started",
        audit_id=audit_id,
        url=url,
        model=model,
    )

    with track_gpt_duration(model=model) as metrics:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are Website Wizard, a production SaaS website "
                            "audit analyst. Provide concise, actionable, prioritized "
                            "recommendations based on Lighthouse data."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Website URL: {url}\n\n"
                            f"Lighthouse JSON:\n{lighthouse_result}"
                        ),
                    },
                ],
                temperature=0.2,
            )

            usage = _extract_usage(response)

            record_gpt_tokens(
                model=model,
                prompt_tokens=usage["prompt_tokens"],
                completion_tokens=usage["completion_tokens"],
                total_tokens=usage["total_tokens"],
            )

            content = response.choices[0].message.content or ""

            metrics["status"] = "success"

            logger.info(
                "GPT analysis completed",
                audit_id=audit_id,
                url=url,
                model=model,
                prompt_tokens=usage["prompt_tokens"],
                completion_tokens=usage["completion_tokens"],
                total_tokens=usage["total_tokens"],
            )

            return {
                "model": model,
                "content": content,
                "usage": usage,
            }

        except Exception as exc:
            metrics["status"] = "failure"

            logger.exception(
                "GPT analysis failed",
                audit_id=audit_id,
                url=url,
                model=model,
                failure_type=exc.__class__.__name__,
            )

            raise
