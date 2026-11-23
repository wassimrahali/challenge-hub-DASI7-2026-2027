from app.clients.base import BaseClient
from app.schemas.external import CasDeTestDTO


class ProblemesClient(BaseClient):
    service_name = "MS3 Problèmes"

    async def get_tests(self, probleme_id: str) -> list[CasDeTestDTO]:
        """GET /api/problemes/{id}/tests (interne, tests cachés inclus)."""
        response = await self._request("GET", f"/api/problemes/{probleme_id}/tests")
        return [CasDeTestDTO.model_validate(item) for item in response.json()]
