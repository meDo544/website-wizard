# backend/utils/upgrade.py

def upgrade_response(
    message,
    current,
    limit,
    recommended_plan="pro",
):
    return {
        "success": False,
        "upgrade_required": True,
        "message": message,
        "current": current,
        "limit": limit,
        "recommended_plan": recommended_plan,
    }
