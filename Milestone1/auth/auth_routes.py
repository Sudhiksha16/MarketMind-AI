# auth_routes.py
# ---------------------------------------------------------
# This file handles user login.
#
# Login flow:
#
# Email + Password
#       ↓
# Find the user
#       ↓
# Check password
#       ↓
# Create JWT token
#       ↓
# Return token + role
# ---------------------------------------------------------

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .auth_utils import verify_password, create_access_token


# Create a router specifically for authentication APIs.
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ---------------------------------------------------------
# DEMO USERS
# ---------------------------------------------------------
# For Milestone 1, we are keeping a small set of users
# directly in Python instead of using the database.
#
# All four demo users use the same password:
# password123
#
# The password itself is NOT stored here.
# Instead, we store its bcrypt hash.
# ---------------------------------------------------------

# IMPORTANT:
# Replace YOUR_BCRYPT_HASH_HERE with the hash you just
# generated in PowerShell.
PASSWORD_HASH = "$2b$12$4dOFZ3POsrdIuHQTBVPUkOGLBQ0U7G9Hqfr19rQ25Fefc8kSizJWS"


DEMO_USERS = {

    "owner@marketmind.com": {
        "email": "owner@marketmind.com",
        "password_hash": PASSWORD_HASH,
        "role": "Business Owner"
    },

    "manager@marketmind.com": {
        "email": "manager@marketmind.com",
        "password_hash": PASSWORD_HASH,
        "role": "Store Manager"
    },

    "sales@marketmind.com": {
        "email": "sales@marketmind.com",
        "password_hash": PASSWORD_HASH,
        "role": "Sales Executive"
    },

    "admin@marketmind.com": {
        "email": "admin@marketmind.com",
        "password_hash": PASSWORD_HASH,
        "role": "Administrator"
    }
}


# ---------------------------------------------------------
# LOGIN REQUEST
# ---------------------------------------------------------
# FastAPI will expect the frontend to send:
#
# {
#     "email": "...",
#     "password": "..."
# }
# ---------------------------------------------------------

class LoginRequest(BaseModel):

    email: str
    password: str


# ---------------------------------------------------------
# LOGIN ENDPOINT
# ---------------------------------------------------------

@router.post("/login")
def login(user: LoginRequest):

    # Search for the user using the email address.
    stored_user = DEMO_USERS.get(user.email)

    # If the email does not exist, reject the login.
    if stored_user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Compare the entered password with the stored
    # bcrypt password hash.
    password_is_valid = verify_password(
        user.password,
        stored_user["password_hash"]
    )

    # If the password is incorrect, reject the login.
    if not password_is_valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Create a JWT token containing the user's email
    # and role.
    access_token = create_access_token(
        email=stored_user["email"],
        role=stored_user["role"]
    )

    # Return the login result to the frontend.
    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "role": stored_user["role"]
    }