"""Tables executions et resultats_test

Revision ID: 0001
Revises:
Create Date: 2026-11-23
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

STATUT_EXECUTION = ("EN_ATTENTE", "EN_COURS", "TERMINEE", "ERREUR")
VERDICT = ("ACCEPTED", "WRONG_ANSWER", "TIMEOUT", "RUNTIME_ERROR", "COMPILATION_ERROR")
STATUT_TEST = (
    "PASSED",
    "WRONG_ANSWER",
    "TIMEOUT",
    "RUNTIME_ERROR",
    "MEMORY_LIMIT",
    "COMPILATION_ERROR",
)


def upgrade() -> None:
    op.create_table(
        "executions",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("soumission_id", sa.String(64), nullable=False),
        sa.Column("probleme_id", sa.String(64), nullable=False),
        sa.Column("equipe_id", sa.String(64), nullable=False),
        sa.Column("hackathon_id", sa.String(64), nullable=False),
        sa.Column(
            "statut",
            sa.Enum(*STATUT_EXECUTION, name="statut_execution"),
            nullable=False,
            server_default="EN_ATTENTE",
        ),
        sa.Column("verdict", sa.Enum(*VERDICT, name="verdict"), nullable=True),
        sa.Column("pourcentage", sa.Numeric(5, 2), nullable=False, server_default="0"),
        sa.Column("duree_ms", sa.Integer(), nullable=True),
        sa.Column("message_erreur", sa.Text(), nullable=True),
        sa.Column("score_transmis", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("score_transmis_le", sa.DateTime(), nullable=True),
        sa.Column("tentatives_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("cree_le", sa.DateTime(), nullable=False),
        sa.Column("executee_le", sa.DateTime(), nullable=True),
        sa.Column("mis_a_jour_le", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("soumission_id", name="uq_executions_soumission"),
    )
    op.create_index(
        "ix_executions_probleme_pct", "executions", ["probleme_id", "pourcentage"]
    )
    op.create_index(
        "ix_executions_score_a_envoyer", "executions", ["statut", "score_transmis"]
    )

    op.create_table(
        "resultats_test",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "execution_id",
            sa.BigInteger(),
            sa.ForeignKey("executions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("cas_de_test_id", sa.String(64), nullable=False),
        sa.Column("statut", sa.Enum(*STATUT_TEST, name="statut_test"), nullable=False),
        sa.Column("poids", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("visible", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("temps_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("sortie_tronquee", sa.Text(), nullable=True),
        sa.UniqueConstraint(
            "execution_id", "cas_de_test_id", name="uq_resultats_execution_test"
        ),
    )


def downgrade() -> None:
    op.drop_table("resultats_test")
    op.drop_index("ix_executions_score_a_envoyer", table_name="executions")
    op.drop_index("ix_executions_probleme_pct", table_name="executions")
    op.drop_table("executions")
