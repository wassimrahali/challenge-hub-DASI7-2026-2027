from fastapi import APIRouter, BackgroundTasks, Depends

from app.api.deps import get_container, get_execution_service
from app.core.container import Container
from app.core.errors import NotFoundError
from app.schemas.errors import ErrorResponse
from app.schemas.execution import (
    ExecutionAccepted,
    ExecutionOut,
    ExecutionRequest,
    to_execution_out,
)
from app.services.execution_service import ExecutionService
from app.tasks.run_execution import run_execution_task

router = APIRouter(prefix="/api/executions", tags=["Exécutions"])


@router.post(
    "",
    status_code=202,
    response_model=ExecutionAccepted,
    summary="Lancer l'exécution d'une soumission (interne, appelé par MS4)",
    responses={
        400: {"model": ErrorResponse, "description": "Corps invalide"},
        404: {"model": ErrorResponse, "description": "Soumission inconnue de MS4"},
        409: {
            "model": ErrorResponse,
            "description": "Une exécution existe déjà pour cette soumission",
        },
        503: {"model": ErrorResponse, "description": "MS4 indisponible"},
    },
)
async def lancer_execution(
    body: ExecutionRequest,
    background: BackgroundTasks,
    service: ExecutionService = Depends(get_execution_service),
    container: Container = Depends(get_container),
) -> ExecutionAccepted:
    execution, soumission = await service.accept(body.soumission_id)
    background.add_task(run_execution_task, container, body.soumission_id, soumission)
    return ExecutionAccepted(soumissionId=execution.soumission_id, statut=execution.statut)


@router.get(
    "/{soumission_id}",
    response_model=ExecutionOut,
    summary="Verdict, pourcentage et résultat par test",
    responses={404: {"model": ErrorResponse, "description": "Aucune exécution pour cette soumission"}},
)
def lire_execution(
    soumission_id: str,
    service: ExecutionService = Depends(get_execution_service),
) -> ExecutionOut:
    execution = service.repo.get_by_soumission(soumission_id)
    if execution is None:
        raise NotFoundError(f"Aucune exécution pour la soumission {soumission_id}")
    return to_execution_out(execution)
