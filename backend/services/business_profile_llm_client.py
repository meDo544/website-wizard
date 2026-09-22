from __future__ import annotations

import os
from typing import Any

from openai import OpenAI


def get_business_profile_client() -> OpenAI:
    return OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )


def get_business_profile_model() -> str:
    return os.getenv(
        "OPENAI_MODEL",
        "gpt-4.1-mini",
    )


def extract_business_profile_usage(
    response: Any,
) -> dict[str, int]:
    usage = getattr(
        response,
        "usage",
        None,
    )

    if usage is None:
        return {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        }

    return {
        "prompt_tokens": int(
            getattr(
                usage,
                "prompt_tokens",
                0,
            )
            or 0
        ),
        "completion_tokens": int(
            getattr(
                usage,
                "completion_tokens",
                0,
            )
            or 0
        ),
        "total_tokens": int(
            getattr(
                usage,
                "total_tokens",
                0,
            )
            or 0
        ),
    }


def generate_business_profile_content(
    *,
    system_prompt: str,
    prompt: str,
    business_type: str,
    model: str,
) -> tuple[str, dict[str, int]]:
    client = get_business_profile_client()

    response = client.chat.completions.create(
        model=model,
        temperature=0.7,
        response_format={
            "type": "json_object"
        },
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": (
                    f"Business Type: {business_type}\n\n"
                    f"Business Description:\n{prompt}"
                ),
            },
        ],
    )

    usage = extract_business_profile_usage(
        response
    )

    content = (
        response.choices[0].message.content
        or "{}"
    )

    return content, usage
