"""Tâche de fond lancée après la réponse 202."""
import logging

from app.core.container import Container
from app.schemas.external import SoumissionDTO
from app.services.execution_service import ExecutionService

logger = logging.getLogger(__name__)


async def run_execution_task(
    container: Container, soumission_id: str, soumission: SoumissionDTO
) -> None:
    # Session dédiée : celle de la requête HTTP est déjà fermée.
    session = container.session_factory()
    try:
        await ExecutionService(session, container).process(soumission_id, soumission)
    except Exception:  # noqa: BLE001
        logger.exception("Tâche d'exécution %s interrompue", soumission_id)
    finally:
        session.close()
