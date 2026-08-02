"""PostgreSQL-backed user persistence layer."""
from typing import Optional
import psycopg2.extras
from .models import User
from .db import get_connection, close


def _dict_row(cursor, columns, row):
    """Convert a tuple row into a dict."""
    if row is None:
        return None
    return dict(zip(columns, row))


class UserStore:
    """Handles user CRUD operations via psycopg2 direct SQL."""

    COLUMNS = ["id", "username", "password_hash", "token"]

    def __init__(self, conn=None):
        """Optionally accept an existing connection for transaction control."""
        self._conn = conn

    def _ensure_conn(self):
        """Ensure a connection is available."""
        if self._conn is None or self._conn.closed:
            self._conn = get_connection()

    def find_by_username(self, username: str) -> Optional[User]:
        """Find a user by username. Returns None if not found."""
        self._ensure_conn()
        cur = self._conn.cursor()
        try:
            cur.execute(
                "SELECT id, username, password_hash, token FROM users WHERE username = %s;",
                (username,),
            )
            row = cur.fetchone()
            if row is None:
                return None
            return User.from_row(_dict_row(cur, self.COLUMNS, row))
        finally:
            cur.close()

    def find_by_token(self, token: str) -> Optional[User]:
        """Find a user by session token. Returns None if not found."""
        self._ensure_conn()
        cur = self._conn.cursor()
        try:
            cur.execute(
                "SELECT id, username, password_hash, token FROM users WHERE token = %s;",
                (token,),
            )
            row = cur.fetchone()
            if row is None:
                return None
            return User.from_row(_dict_row(cur, self.COLUMNS, row))
        finally:
            cur.close()

    def update_token(self, username: str, token: str) -> None:
        """Update the session token for a specific user."""
        self._ensure_conn()
        cur = self._conn.cursor()
        try:
            cur.execute(
                "UPDATE users SET token = %s WHERE username = %s;",
                (token, username),
            )
            self._conn.commit()
        finally:
            cur.close()

    def clear_token(self, token: str) -> None:
        """Clear (set to NULL) the session token matching the given token."""
        self._ensure_conn()
        cur = self._conn.cursor()
        try:
            cur.execute(
                "UPDATE users SET token = NULL WHERE token = %s;",
                (token,),
            )
            self._conn.commit()
        finally:
            cur.close()

    def close(self):
        """Close the store's connection if it owns one."""
        if self._conn is not None and not self._conn.closed:
            self._conn.close()
