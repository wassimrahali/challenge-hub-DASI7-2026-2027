from app.clients.base import BaseClient
from app.schemas.external import SoumissionDTO, StatutSoumission, StatutUpdate


class SoumissionsClient(BaseClient):
    service_name = "MS4 Soumissions"

    async def get_soumission(self, soumission_id: str) -> SoumissionDTO:
        """GET /api/soumissions/{id}"""
        response = await self._request("GET", f"/api/soumissions/{soumission_id}")
        return SoumissionDTO.model_validate(response.json())

    async def update_statut(self, soumission_id: str, statut: StatutSoumission) -> None:
        """PATCH /api/soumissions/{id}/statut (interne)."""
        body = StatutUpdate(statut=statut).model_dump(mode="json")
        await self._request("PATCH", f"/api/soumissions/{soumission_id}/statut", json=body)
