"""Orchestration du flux d'exécution d'une soumission."""
import asyncio
import logging
import time

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.container import Container
from app.core.errors import AppError, ConflictError
from app.executor.base import ExecutionLimits, TestCase
from app.models import Execution, ResultatTest, StatutExecution
from app.repositories.execution_repository import ExecutionRepository
from app.schemas.external import (
    CasDeTestDTO,
    ScorePayload,
    SoumissionDTO,
    StatutSoumission,
)
from app.services.scoring import calculer_pourcentage, determiner_verdict

logger = logging.getLogger(__name__)


class ExecutionService:
    def __init__(self, session: Session, container: Container) -> None:
        self.session = session
        self.c = container
        self.repo = ExecutionRepository(session)

    # ------------------------------------------------------------------
    # Étape synchrone (requête POST) : valider, enregistrer, répondre 202
    # ------------------------------------------------------------------
    async def accept(self, soumission_id: str) -> tuple[Execution, SoumissionDTO]:
        """Vérifie la soumission dans MS4 et crée l'exécution EN_ATTENTE.

        Idempotence : une seule ligne par soumission (contrainte d'unicité).
        - EN_ATTENTE / EN_COURS / TERMINEE -> 409 (aucun doublon)
        - ERREUR -> relance autorisée, la même ligne est réinitialisée
        Lève NotFoundError (404) si MS4 ne connaît pas la soumission,
        ServiceUnavailableError (503) si MS4 reste injoignable.
        """
        existing = self.repo.get_by_soumission(soumission_id)
        if existing is not None and existing.statut is not StatutExecution.ERREUR:
            raise ConflictError(
                f"Une exécution existe déjà pour la soumission {soumission_id}",
                {"statut": existing.statut.value},
            )

        soumission = await self.c.ms4.get_soumission(soumission_id)
        try:
            if existing is None:
                execution = self.repo.create(
                    soumission_id=soumission_id,
                    probleme_id=soumission.probleme_id,
                    equipe_id=soumission.equipe_id,
                    hackathon_id=soumission.hackathon_id,
                )
            else:
                execution = existing
                self.repo.reset(
                    execution,
                    probleme_id=soumission.probleme_id,
                    equipe_id=soumission.equipe_id,
                    hackathon_id=soumission.hackathon_id,
                )
            self.session.commit()
        except IntegrityError as exc:  # deux POST simultanés
            self.session.rollback()
            raise ConflictError(
                f"Une exécution existe déjà pour la soumission {soumission_id}"
            ) from exc
        return execution, soumission

    # ------------------------------------------------------------------
    # Étape asynchrone (tâche de fond)
    # ------------------------------------------------------------------
    async def process(self, soumission_id: str, soumission: SoumissionDTO) -> None:
        execution = self.repo.get_by_soumission(soumission_id)
        if execution is None or execution.statut is not StatutExecution.EN_ATTENTE:
            logger.info("Exécution %s ignorée (absente ou déjà prise en charge)", soumission_id)
            return

        self.repo.mark_running(execution)
        self.session.commit()

        try:
            tests = await self.c.ms3.get_tests(soumission.probleme_id)
            if not tests:
                raise AppError(f"Aucun test pour le problème {soumission.probleme_id}")

            started = time.perf_counter()
            runs = await asyncio.to_thread(self._run_all, soumission, tests)
            duree_ms = int((time.perf_counter() - started) * 1000)

            resultats = [
                ResultatTest(
                    cas_de_test_id=test.id,
                    statut=run.statut,
                    poids=test.poids,
                    visible=test.visible,
                    temps_ms=run.temps_ms,
                    sortie_tronquee=run.sortie,
                )
                for test, run in runs
            ]
            self.repo.save_results(
                execution,
                resultats=resultats,
                verdict=determiner_verdict(r.statut for r in resultats),
                pourcentage=calculer_pourcentage((r.poids, r.statut) for r in resultats),
                duree_ms=duree_ms,
            )
            self.session.commit()
        except Exception as exc:  # noqa: BLE001 - toute panne marque l'exécution en ERREUR
            logger.exception("Échec de l'exécution %s", soumission_id)
            self.session.rollback()
            execution = self.repo.get_by_soumission(soumission_id)
            self.repo.mark_error(execution, str(exc)[:1000])
            self.session.commit()
            await self._notify_ms4(soumission_id, StatutSoumission.ERREUR)
            return

        await self._notify_ms4(soumission_id, StatutSoumission.EXECUTEE)
        await self.push_score(execution)

    def _run_all(
        self, soumission: SoumissionDTO, tests: list[CasDeTestDTO]
    ) -> list[tuple[CasDeTestDTO, "TestRunResult"]]:  # noqa: F821
        s = self.c.settings
        results = []
        for test in tests:
            limits = ExecutionLimits(
                time_limit_ms=test.temps_limite_ms or s.default_time_limit_ms,
                memory_limit_mb=test.memoire_limite_mb or s.default_memory_limit_mb,
                max_output_chars=s.max_output_chars,
            )
            run = self.c.executor.run_test(
                code=soumission.code,
                langage=soumission.langage,
                test_case=TestCase(id=test.id, input=test.input, expected_output=test.output),
                limits=limits,
            )
            results.append((test, run))
        return results

    # ------------------------------------------------------------------
    # Notifications sortantes
    # ------------------------------------------------------------------
    async def _notify_ms4(self, soumission_id: str, statut: StatutSoumission) -> None:
        try:
            await self.c.ms4.update_statut(soumission_id, statut)
        except Exception as exc:  # noqa: BLE001
            logger.error("MS4 non notifié pour %s (%s) : %s", soumission_id, statut.value, exc)

    async def push_score(self, execution: Execution) -> bool:
        """Envoie le score à MS6. En cas d'échec il reste `score_transmis = false`
        et sera renvoyé par la tâche planifiée."""
        payload = ScorePayload(
            hackathonId=execution.hackathon_id,
            equipeId=execution.equipe_id,
            problemeId=execution.probleme_id,
            soumissionId=execution.soumission_id,
            pourcentage=execution.pourcentage,
        )
        try:
            await self.c.ms6.send_score(payload)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Score de %s non transmis à MS6 : %s", execution.soumission_id, exc)
            self.repo.record_score_attempt(execution, success=False)
            self.session.commit()
            return False
        self.repo.record_score_attempt(execution, success=True)
        self.session.commit()
        return True

    async def retry_pending_scores(self) -> int:
        """Renvoie à MS6 les scores non transmis. Retourne le nombre envoyé."""
        sent = 0
        for execution in self.repo.list_scores_a_envoyer(self.c.settings.score_retry_batch):
            if await self.push_score(execution):
                sent += 1
        return sent
