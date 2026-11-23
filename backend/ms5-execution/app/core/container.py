"""Conteneur de dépendances partagé (stocké dans app.state)."""
from dataclasses import dataclass
from typing import Callable

from sqlalchemy.orm import Session

from app.clients.ms3_problemes import ProblemesClient
from app.clients.ms4_soumissions import SoumissionsClient
from app.clients.ms6_classement import ClassementClient
from app.core.config import Settings
from app.executor.base import CodeExecutor


@dataclass
class Container:
    settings: Settings
    session_factory: Callable[[], Session]
    ms3: ProblemesClient
    ms4: SoumissionsClient
    ms6: ClassementClient
    executor: CodeExecutor
