# auth_utils.py
# ---------------------------------------------------------
# This file contains the basic authentication utilities.
#
# Authentication means:
# "Who is the user?"
#
# We will:
# 1. Store passwords in hashed form.
# 2. Check a user's password during login.
# 3. Create a JWT token after successful login.
# 4. Read the user information from the JWT token.
# ---------------------------------------------------------

from datetime import datetime, timedelta, timezone

# Used for creating and verifying JWT tokens.
from jose import jwt

# Used for securely hashing passwords.
from passlib.context import CryptContext


# ---------------------------------------------------------
# SECRET KEY
# ---------------------------------------------------------
# JWT uses this secret key to sign tokens.
#
# For our Milestone 1 local demo, we keep it here.
# In a real production application, this should be stored
# in an environment variable.
# ---------------------------------------------------------

SECRET_KEY = "marketmind-milestone1-secret-key"

# Algorithm used to sign the JWT token.
ALGORITHM = "HS256"

# Token will remain valid for 60 minutes.
ACCESS_TOKEN_EXPIRE_MINUTES = 60


# ---------------------------------------------------------
# PASSWORD HASHING
# ---------------------------------------------------------
# bcrypt is used to convert a normal password into a
# secure-looking hash.
#
# We NEVER need to store the original password.
# ---------------------------------------------------------

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    """
    Convert a normal password into a secure hash.
    """

    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Check whether the entered password matches
    the stored hashed password.
    """

    return pwd_context.verify(password, hashed_password)


# ---------------------------------------------------------
# JWT TOKEN CREATION
# ---------------------------------------------------------

def create_access_token(email: str, role: str) -> str:
    """
    Create a JWT token containing:
    - user's email
    - user's role
    - token expiration time
    """

    # Calculate when the token should expire.
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    # Information stored inside the JWT token.
    payload = {
        "sub": email,       # "sub" identifies the user
        "role": role,       # Stores the user's role
        "exp": expire       # Token expiration time
    }

    # Create and return the signed JWT token.
    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


# ---------------------------------------------------------
# JWT TOKEN VERIFICATION
# ---------------------------------------------------------

def decode_access_token(token: str):
    """
    Decode a JWT token and return the information
    stored inside it.

    If the token is invalid, an exception will occur.
    """

    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM]
    )

    return payload