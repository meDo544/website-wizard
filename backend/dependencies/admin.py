from fastapi import Depends, HTTPException, status

from backend.dependencies.auth import get_current_user

from backend.models.user import User


def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Ensures the current user has admin role.
    """

    # ---------------------------------
    # Check roles
    # ---------------------------------

    role_names = [
        role.name.lower()
        for role in current_user.roles
    ]

    if "admin" not in role_names:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )

    return current_user
