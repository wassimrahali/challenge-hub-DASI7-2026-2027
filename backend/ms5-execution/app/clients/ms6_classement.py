from app.clients.base import BaseClient
from app.schemas.external import ScorePayload


class ClassementClient(BaseClient):
    service_name = "MS6 Classement"

    async def send_score(self, payload: ScorePayload) -> None:
        """POST /api/classements/scores (interne)."""
        body = payload.model_dump(mode="json", by_alias=True)
        await self._request("POST", "/api/classements/scores", json=body)
