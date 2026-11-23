"""Contrats de l'API d'exécution (JSON en camelCase, comme les autres services)."""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import StatutExecution, StatutTest, Verdict


class ExecutionRequest(BaseModel):
    """Corps de POST /api/executions."""

    soumission_id: str = Field(
        alias="soumissionId", min_length=1, max_length=64, examples=["665f1c2e9b1d4a0012ab34cd"]
    )

    model_config = ConfigDict(populate_by_name=True)


class ExecutionAccepted(BaseModel):
    """Réponse 202 : le traitement continue en arrière-plan."""

    soumission_id: str = Field(alias="soumissionId")
    statut: StatutExecution

    model_config = ConfigDict(populate_by_name=True)


class ResultatTestOut(BaseModel):
    """Résultat d'un test. Pour un test caché, seuls le statut, le poids et le temps sont exposés."""

    cas_de_test_id: str | None = Field(alias="casDeTestId")
    statut: StatutTest
    poids: int
    temps_ms: int = Field(alias="tempsMs")
    visible: bool
    sortie: str | None = None

    model_config = ConfigDict(populate_by_name=True)


class ExecutionOut(BaseModel):
    """Réponse de GET /api/executions/{soumissionId}."""

    soumission_id: str = Field(alias="soumissionId")
    statut: StatutExecution
    verdict: Verdict | None = None
    pourcentage: Decimal
    duree_ms: int | None = Field(default=None, alias="dureeMs")
    executee_le: datetime | None = Field(default=None, alias="executeeLe")
    score_transmis: bool = Field(alias="scoreTransmis")
    message_erreur: str | None = Field(default=None, alias="messageErreur")
    resultats: list[ResultatTestOut] = []

    model_config = ConfigDict(populate_by_name=True)


def to_execution_out(execution) -> ExecutionOut:
    """Convertit une entité Execution en réponse, en masquant les tests cachés."""
    resultats = [
        ResultatTestOut(
            casDeTestId=r.cas_de_test_id if r.visible else None,
            statut=r.statut,
            poids=r.poids,
            tempsMs=r.temps_ms,
            visible=r.visible,
            sortie=r.sortie_tronquee if r.visible else None,
        )
        for r in execution.resultats
    ]
    return ExecutionOut(
        soumissionId=execution.soumission_id,
        statut=execution.statut,
        verdict=execution.verdict,
        pourcentage=execution.pourcentage,
        dureeMs=execution.duree_ms,
        executeeLe=execution.executee_le,
        scoreTransmis=execution.score_transmis,
        messageErreur=execution.message_erreur,
        resultats=resultats,
    )
