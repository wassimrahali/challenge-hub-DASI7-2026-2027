"""Accès aux données : seul endroit qui écrit du SQL / des requêtes ORM."""
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.base import utcnow
from app.models import Execution, ResultatTest, StatutExecution, Verdict


class ExecutionRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    # --- lecture -----------------------------------------------------------
    def get_by_soumission(self, soumission_id: str) -> Execution | None:
        stmt = (
            select(Execution)
            .where(Execution.soumission_id == soumission_id)
            .options(selectinload(Execution.resultats))
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def list_scores_a_envoyer(self, limit: int) -> list[Execution]:
        stmt = (
            select(Execution)
            .where(
                Execution.statut == StatutExecution.TERMINEE,
                Execution.score_transmis.is_(False),
            )
            .order_by(Execution.id)
            .limit(limit)
        )
        return list(self.session.execute(stmt).scalars())

    # --- écriture (flush uniquement ; le commit est fait par le service) ----
    def create(
        self, *, soumission_id: str, probleme_id: str, equipe_id: str, hackathon_id: str
    ) -> Execution:
        execution = Execution(
            soumission_id=soumission_id,
            probleme_id=probleme_id,
            equipe_id=equipe_id,
            hackathon_id=hackathon_id,
            statut=StatutExecution.EN_ATTENTE,
        )
        self.session.add(execution)
        self.session.flush()
        return execution

    def reset(self, execution: Execution, *, probleme_id: str, equipe_id: str, hackathon_id: str) -> None:
        """Remet une exécution en ERREUR à l'état EN_ATTENTE (réutilise la même ligne)."""
        execution.resultats.clear()
        execution.probleme_id = probleme_id
        execution.equipe_id = equipe_id
        execution.hackathon_id = hackathon_id
        execution.statut = StatutExecution.EN_ATTENTE
        execution.verdict = None
        execution.pourcentage = Decimal("0")
        execution.duree_ms = None
        execution.message_erreur = None
        execution.score_transmis = False
        execution.score_transmis_le = None
        execution.tentatives_score = 0
        execution.executee_le = None
        self.session.flush()

    def mark_running(self, execution: Execution) -> None:
        execution.statut = StatutExecution.EN_COURS
        self.session.flush()

    def save_results(
        self,
        execution: Execution,
        *,
        resultats: list[ResultatTest],
        verdict: Verdict,
        pourcentage: Decimal,
        duree_ms: int,
    ) -> None:
        execution.resultats.clear()
        execution.resultats.extend(resultats)
        execution.verdict = verdict
        execution.pourcentage = pourcentage
        execution.duree_ms = duree_ms
        execution.statut = StatutExecution.TERMINEE
        execution.executee_le = utcnow()
        self.session.flush()

    def mark_error(self, execution: Execution, message: str) -> None:
        execution.statut = StatutExecution.ERREUR
        execution.message_erreur = message
        execution.executee_le = utcnow()
        self.session.flush()

    def record_score_attempt(self, execution: Execution, *, success: bool) -> None:
        execution.tentatives_score += 1
        if success:
            execution.score_transmis = True
            execution.score_transmis_le = utcnow()
        self.session.flush()
