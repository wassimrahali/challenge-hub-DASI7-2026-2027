import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routers import executions, health
from app.clients.ms3_problemes import ProblemesClient
from app.clients.ms4_soumissions import SoumissionsClient
from app.clients.ms6_classement import ClassementClient
from app.core import eureka
from app.core.config import get_settings
from app.core.container import Container
from app.core.errors import register_error_handlers
from app.core.logging import setup_logging
from app.db.session import SessionLocal
from app.executor.factory import create_executor
from app.tasks.retry_scores import create_scheduler

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    container = Container(
        settings=settings,
        session_factory=SessionLocal,
        ms3=ProblemesClient(settings.ms3_url, settings),
        ms4=SoumissionsClient(settings.ms4_url, settings),
        ms6=ClassementClient(settings.ms6_url, settings),
        executor=create_executor(),
    )
    app.state.container = container

    scheduler = None
    if settings.scheduler_enabled:
        scheduler = create_scheduler(container)
        scheduler.start()

    registered = await eureka.register(settings)
    logger.info("%s démarré sur le port %s", settings.app_name, settings.app_port)
    try:
        yield
    finally:
        if scheduler:
            scheduler.shutdown(wait=False)
        if registered:
            await eureka.deregister()
        await container.ms3.aclose()
        await container.ms4.aclose()
        await container.ms6.aclose()


app = FastAPI(
    title="MS5 - Exécution",
    description=(
        "Exécute le code soumis contre les tests d'un problème et calcule le "
        "pourcentage de réussite. Service interne de ChallengeHub."
    ),
    version="0.1.0",
    lifespan=lifespan,
)
register_error_handlers(app)
app.include_router(health.router)
app.include_router(executions.router)


if __name__ == "__main__":
    import uvicorn

    s = get_settings()
    uvicorn.run("app.main:app", host=s.app_host, port=s.app_port)
