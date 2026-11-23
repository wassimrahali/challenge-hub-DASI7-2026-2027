from datetime import datetime, timezone

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


def utcnow() -> datetime:
    """Date UTC sans fuseau (les colonnes DATETIME MySQL sont naïves)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
