def build_usage_warning(current, limit):
    """
    Returns warning payload if usage exceeds 80%.
    """

    if limit <= 0:
        return None

    usage_ratio = current / limit

    if usage_ratio >= 0.8:
        return {
            "warning": True,
            "message": f"You've used {current}/{limit} of your plan limit.",
            "usage_percent": round(usage_ratio * 100),
        }

    return None
