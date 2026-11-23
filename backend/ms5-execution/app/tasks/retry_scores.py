"""Tâche planifiée : renvoie à MS6 les scores restés à transmettre."""
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.container import Container
from app.services.execution_service import ExecutionService

logger = logging.getLogger(__name__)


async def retry_scores_job(container: Container) -> None:
    session = container.session_factory()
    try:
        sent = await ExecutionService(session, container).retry_pending_scores()
        if sent:
            logger.info("%d score(s) renvoyé(s) à MS6", sent)
    except Exception:  # noqa: BLE001
        logger.exception("Renvoi des scores interrompu")
    finally:
        session.close()


def create_scheduler(container: Container) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        retry_scores_job,
        "interval",
        seconds=container.settings.score_retry_interval_s,
        args=[container],
        id="retry-scores",
        max_instances=1,
        coalesce=True,
    )
    return scheduler
