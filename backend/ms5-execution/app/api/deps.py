from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.container import Container
from app.db.session import get_db
from app.services.execution_service import ExecutionService


def get_container(request: Request) -> Container:
    return request.app.state.container


def get_execution_service(
    session: Session = Depends(get_db),
    container: Container = Depends(get_container),
) -> ExecutionService:
    return ExecutionService(session, container)
