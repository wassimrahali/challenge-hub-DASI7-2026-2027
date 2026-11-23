from sqlalchemy import (
    BigInteger,
    Boolean,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import StatutTest


class ResultatTest(Base):
    __tablename__ = "resultats_test"
    __table_args__ = (
        UniqueConstraint("execution_id", "cas_de_test_id", name="uq_resultats_execution_test"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True
    )
    # FK locale (même base) ; cas_de_test_id vient de MS3, sans FK.
    execution_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("executions.id", ondelete="CASCADE"), nullable=False
    )
    cas_de_test_id: Mapped[str] = mapped_column(String(64), nullable=False)
    statut: Mapped[StatutTest] = mapped_column(
        SAEnum(StatutTest, name="statut_test", values_callable=lambda e: [m.value for m in e]),
        nullable=False,
    )
    poids: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    visible: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="1"
    )
    temps_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    sortie_tronquee: Mapped[str | None] = mapped_column(Text, nullable=True)

    execution: Mapped["Execution"] = relationship(back_populates="resultats")  # noqa: F821
