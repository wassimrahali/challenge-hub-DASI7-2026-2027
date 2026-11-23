"""Configuration par variables d'environnement, compatible Config Server.

Ordre de priorité (du plus fort au plus faible) :
1. variables d'environnement réelles
2. fichier .env
3. Config Server (Spring Cloud Config), si CONFIG_SERVER_URL est défini
4. valeurs par défaut ci-dessous

Les propriétés du Config Server sont converties en variables d'environnement :
``ms3.url`` devient ``MS3_URL``, ``http-timeout-s`` devient ``HTTP_TIMEOUT_S``.
"""
import logging
import os
import re
from functools import lru_cache

import httpx
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Service
    app_name: str = "execution-service"
    app_host: str = "0.0.0.0"
    app_port: int = 8085
    app_profile: str = "default"

    # Base de données
    database_url: str = "mysql+pymysql://root:password@localhost:3306/execution_db"

    # Config Server (vide = désactivé)
    config_server_url: str = ""

    # Eureka
    eureka_enabled: bool = True
    eureka_server: str = "http://localhost:8761/eureka/"
    instance_host: str = ""

    # Services appelés
    ms3_url: str = "http://localhost:8083"
    ms4_url: str = "http://localhost:8084"
    ms6_url: str = "http://localhost:8086"

    # Résilience des appels sortants
    http_timeout_s: float = 5.0
    http_max_attempts: int = 4
    http_backoff_base_s: float = 0.5

    # Exécution
    default_time_limit_ms: int = 2000
    default_memory_limit_mb: int = 256
    max_output_chars: int = 2000

    # Renvoi des scores vers MS6
    scheduler_enabled: bool = True
    score_retry_interval_s: int = 60
    score_retry_batch: int = 50


def _to_env_key(prop: str) -> str:
    return re.sub(r"[.\-]", "_", prop).upper()


def load_from_config_server() -> None:
    """Récupère la configuration du Config Server et la place dans os.environ.

    Meilleur effort : si le serveur est absent, on continue avec l'environnement local.
    Les variables déjà définies ne sont jamais écrasées.
    """
    base = os.getenv("CONFIG_SERVER_URL", "").rstrip("/")
    if not base:
        return
    app = os.getenv("APP_NAME", "execution-service")
    profile = os.getenv("APP_PROFILE", "default")
    try:
        response = httpx.get(f"{base}/{app}/{profile}", timeout=3.0)
        response.raise_for_status()
        sources = response.json().get("propertySources", [])
    except (httpx.HTTPError, ValueError) as exc:
        logger.warning("Config Server indisponible (%s), configuration locale utilisée", exc)
        return
    # Le Config Server renvoie les sources de la plus prioritaire à la moins prioritaire.
    for source in sources:
        for key, value in source.get("source", {}).items():
            os.environ.setdefault(_to_env_key(key), str(value))
    logger.info("Configuration chargée depuis le Config Server (%d source(s))", len(sources))


@lru_cache
def get_settings() -> Settings:
    load_from_config_server()
    return Settings()
