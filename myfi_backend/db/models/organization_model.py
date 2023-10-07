from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from myfi_backend.db.base import Base


class Organization(Base):
    """Model for organizations."""

    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(String(length=200), unique=True, index=True)
    description: Mapped[str] = mapped_column(String(length=200), nullable=True)
