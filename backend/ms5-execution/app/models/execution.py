from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Enum as SAEnum,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, utcnow
from app.models.enums import StatutExecution, Verdict


def _enum(enum_cls, name: str) -> SAEnum:
    return SAEnum(enum_cls, name=name, values_callable=lambda e: [m.value for m in e])


class Execution(Base):
    __tablename__ = "executions"
    __table_args__ = (
        UniqueConstraint("soumission_id", name="uq_executions_soumission"),
        Index("ix_executions_probleme_pct", "probleme_id", "pourcentage"),
        Index("ix_executions_score_a_envoyer", "statut", "score_transmis"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True
    )
    # Identifiants des autres services : aucune clé étrangère.
    soumission_id: Mapped[str] = mapped_column(String(64), nullable=False)
    probleme_id: Mapped[str] = mapped_column(String(64), nullable=False)
    equipe_id: Mapped[str] = mapped_column(String(64), nullable=False)
    hackathon_id: Mapped[str] = mapped_column(String(64), nullable=False)

    statut: Mapped[StatutExecution] = mapped_column(
        _enum(StatutExecution, "statut_execution"),
        nullable=False,
        default=StatutExecution.EN_ATTENTE,
        server_default=StatutExecution.EN_ATTENTE.value,
    )
    verdict: Mapped[Verdict | None] = mapped_column(_enum(Verdict, "verdict"), nullable=True)
    pourcentage: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False, default=Decimal("0"), server_default="0"
    )
    duree_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    message_erreur: Mapped[str | None] = mapped_column(Text, nullable=True)

    score_transmis: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="0"
    )
    score_transmis_le: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    tentatives_score: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )

    cree_le: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)
    executee_le: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    mis_a_jour_le: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utcnow, onupdate=utcnow
    )

    resultats: Mapped[list["ResultatTest"]] = relationship(  # noqa: F821
        back_populates="execution",
        cascade="all, delete-orphan",
        order_by="ResultatTest.id",
    )
