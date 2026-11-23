"""Client HTTP commun : timeouts, retries avec backoff exponentiel (tenacity)."""
import logging

import httpx
from tenacity import (
    AsyncRetrying,
    RetryError,
    before_sleep_log,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import Settings
from app.core.errors import NotFoundError, ServiceUnavailableError

logger = logging.getLogger(__name__)


class _Retryable(Exception):
    """Erreur transitoire (réseau, timeout, 5xx) : on réessaie."""


class BaseClient:
    service_name = "service"

    def __init__(self, base_url: str, settings: Settings) -> None:
        self._settings = settings
        self._http = httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            timeout=httpx.Timeout(settings.http_timeout_s),
        )

    async def aclose(self) -> None:
        await self._http.aclose()

    async def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Envoie la requête avec retries sur erreurs transitoires.

        - 404 -> NotFoundError (jamais réessayé)
        - autre 4xx -> renvoyé tel quel après raise_for_status (jamais réessayé)
        - réseau / timeout / 5xx -> réessayé, puis ServiceUnavailableError
        """

        async def attempt() -> httpx.Response:
            try:
                response = await self._http.request(method, url, **kwargs)
            except (httpx.TransportError, httpx.TimeoutException) as exc:
                raise _Retryable(f"{type(exc).__name__}: {exc}") from exc
            if response.status_code >= 500:
                raise _Retryable(f"HTTP {response.status_code}")
            return response

        retrying = AsyncRetrying(
            stop=stop_after_attempt(self._settings.http_max_attempts),
            wait=wait_exponential(multiplier=self._settings.http_backoff_base_s, max=10),
            retry=retry_if_exception(lambda e: isinstance(e, _Retryable)),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            reraise=False,
        )
        try:
            response = await retrying(attempt)
        except RetryError as exc:
            cause = exc.last_attempt.exception()
            raise ServiceUnavailableError(
                f"{self.service_name} indisponible ({cause})"
            ) from exc

        if response.status_code == 404:
            raise NotFoundError(f"{self.service_name} : ressource introuvable ({url})")
        response.raise_for_status()
        return response
