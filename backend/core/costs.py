from backend.core.pricing import GPT_PRICING


def calculate_gpt_cost(
    *,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
) -> float:

    pricing = GPT_PRICING.get(model)

    if not pricing:
        return 0.0

    prompt_cost = (
        prompt_tokens / 1000
    ) * pricing["prompt_per_1k"]

    completion_cost = (
        completion_tokens / 1000
    ) * pricing["completion_per_1k"]

    total_cost = (
        prompt_cost
        + completion_cost
    )

    return round(total_cost, 8)
