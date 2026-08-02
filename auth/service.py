import uuid
import bcrypt
from typing import Optional

from .models import User
from .store import UserStore


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against a bcrypt hash."""
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def login(username: str, password: str, store: Optional[UserStore] = None) -> str:
    """Authenticate a user and return a session token.

    Args:
        username: The username.
        password: The password.
        store: Optional UserStore instance. Uses default if not provided.

    Returns:
        A session token string.

    Raises:
        ValueError: If username or password is empty, or credentials are invalid.
    """
    if not username:
        raise ValueError("Username is required.")
    if not password:
        raise ValueError("Password is required.")

    result, token_or_error = authenticate(username, password, store)
    if not result:
        raise ValueError(token_or_error)

    return token_or_error


def authenticate(
    username: str, password: str, store: Optional[UserStore] = None
) -> tuple[bool, str]:
    """Verify credentials and return a structured result.

    Returns:
        A tuple of (success: bool, message_or_token: str).
        On success, the second element is the session token.
        On failure, the second element is the error message.
    """
    if not username:
        return False, "Username is required."
    if not password:
        return False, "Password is required."

    if store is None:
        store = UserStore()

    user = store.find_by_username(username)
    if user is None:
        return False, "Invalid username or password."

    if not verify_password(password, user.password_hash):
        return False, "Invalid username or password."

    token = str(uuid.uuid4())
    store.update_token(username, token)

    return True, token


def get_current_user(token: str, store: Optional[UserStore] = None) -> Optional[User]:
    """Look up the currently authenticated user by session token.

    Returns:
        The User if found, None otherwise.
    """
    if store is None:
        store = UserStore()
    return store.find_by_token(token)


def logout(token: str, store: Optional[UserStore] = None) -> None:
    """Clear the session token, effectively logging out the user.

    Args:
        token: The session token to invalidate.
        store: Optional UserStore instance.

    Raises:
        ValueError: If token is empty.
    """
    if not token:
        raise ValueError("Token is required.")
    if store is None:
        store = UserStore()
    store.clear_token(token)
