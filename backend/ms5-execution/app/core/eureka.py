"""Enregistrement du service dans Eureka (py-eureka-client)."""
import logging

import py_eureka_client.eureka_client as eureka_client

from app.core.config import Settings

logger = logging.getLogger(__name__)


async def register(settings: Settings) -> bool:
    """Enregistre l'instance. Ne bloque jamais le démarrage si Eureka est absent."""
    if not settings.eureka_enabled:
        logger.info("Eureka désactivé")
        return False
    try:
        kwargs: dict = {
            "eureka_server": settings.eureka_server,
            "app_name": settings.app_name,
            "instance_port": settings.app_port,
        }
        if settings.instance_host:
            kwargs["instance_host"] = settings.instance_host
            kwargs["health_check_url"] = (
                f"http://{settings.instance_host}:{settings.app_port}/health"
            )
        await eureka_client.init_async(**kwargs)
        logger.info("Enregistré dans Eureka : %s", settings.eureka_server)
        return True
    except Exception as exc:  # noqa: BLE001 - le service doit démarrer sans Eureka
        logger.warning("Enregistrement Eureka impossible : %s", exc)
        return False


async def deregister() -> None:
    try:
        await eureka_client.stop_async()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Désenregistrement Eureka impossible : %s", exc)
