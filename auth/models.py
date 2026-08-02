from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class User:
    """Represents a system user with authentication credentials, backed by PostgreSQL."""
    username: str
    password_hash: str
    token: Optional[str] = None
    id: Optional[int] = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_row(cls, row: dict) -> "User":
        """Build a User from a psycopg2 RealDictRow or dict."""
        return cls(
            id=row.get("id"),
            username=row["username"],
            password_hash=row["password_hash"],
            token=row.get("token"),
        )
