# rbac.py
# ---------------------------------------------------------
# RBAC = Role-Based Access Control
#
# Authentication tells us WHO the user is.
# RBAC tells us WHAT that user is allowed to do.
#
# Example:
#
# Business Owner → can access business analytics
# Store Manager  → can access store information
# Sales Executive → can access sales operations
# Administrator  → can access administrative features
# ---------------------------------------------------------

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .auth_utils import decode_access_token


# ---------------------------------------------------------
# HTTP BEARER
# ---------------------------------------------------------
# FastAPI uses this to read the JWT token from a request.
#
# The frontend will eventually send:
#
# Authorization: Bearer <JWT_TOKEN>
# ---------------------------------------------------------

security = HTTPBearer()


# ---------------------------------------------------------
# GET CURRENT USER
# ---------------------------------------------------------
# This function:
#
# 1. Receives the JWT token.
# 2. Decodes the token.
# 3. Gets the user's email and role.
# 4. Returns that information.
# ---------------------------------------------------------

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    # Get the actual token from the Authorization header.
    token = credentials.credentials

    try:

        # Decode the JWT token.
        payload = decode_access_token(token)

        # Get email and role from the token.
        email = payload.get("sub")
        role = payload.get("role")

        # Make sure the required information exists.
        if email is None or role is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token"
            )

        # Return the logged-in user's information.
        return {
            "email": email,
            "role": role
        }

    except Exception:

        # If the token is invalid or expired,
        # reject the request.
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


# ---------------------------------------------------------
# ROLE CHECK
# ---------------------------------------------------------
# This function creates a reusable RBAC check.
#
# Example:
#
# @app.get("/admin")
# def admin_page(
#     user=Depends(require_role(["Administrator"]))
# ):
#     ...
#
# Only Administrator users will be allowed.
# ---------------------------------------------------------

def require_role(allowed_roles):

    def role_checker(
        user=Depends(get_current_user)
    ):

        # Check whether the user's role is allowed.
        if user["role"] not in allowed_roles:

            # 403 means:
            # "You are authenticated, but you are
            # not allowed to access this resource."
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this resource"
            )

        # Return the user if the role is allowed.
        return user

    return role_checker