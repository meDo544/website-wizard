"""
OpenAI Pricing Registry

All prices are USD per 1K tokens.
"""

GPT_PRICING = {

    "gpt-4.1-mini": {
        "prompt_per_1k": 0.00015,
        "completion_per_1k": 0.00060,
    },

    "gpt-4.1": {
        "prompt_per_1k": 0.005,
        "completion_per_1k": 0.015,
    },

    "gpt-4o-mini": {
        "prompt_per_1k": 0.00015,
        "completion_per_1k": 0.00060,
    },
}
