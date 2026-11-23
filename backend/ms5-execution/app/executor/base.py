"""Abstraction de l'exécuteur de code.

L'implémentation (sous-processus isolé : limites de temps et de mémoire, sans réseau,
répertoire temporaire jetable, utilisateur sans privilèges) viendra à l'étape suivante.
Le reste du service ne dépend que de cette interface.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.models.enums import StatutTest
from app.schemas.external import Langage


@dataclass(frozen=True)
class ExecutionLimits:
    time_limit_ms: int
    memory_limit_mb: int
    max_output_chars: int
    network_enabled: bool = False


@dataclass(frozen=True)
class TestCase:
    __test__ = False  # n'est pas une classe de tests pytest
    id: str
    input: str
    expected_output: str


@dataclass(frozen=True)
class TestRunResult:
    __test__ = False  # n'est pas une classe de tests pytest
    statut: StatutTest
    temps_ms: int
    sortie: str | None = None


class CodeExecutor(ABC):
    """Exécute un code source sur un test et compare la sortie à l'attendu.

    Contrat :
    - ne lève jamais d'exception pour une erreur du code utilisateur : elle est
      traduite en statut (TIMEOUT, RUNTIME_ERROR, MEMORY_LIMIT, COMPILATION_ERROR) ;
    - ne lève une exception que pour une panne de l'exécuteur lui-même ;
    - l'appel est synchrone et bloquant (le service l'exécute dans un thread) ;
    - `sortie` est tronquée à `limits.max_output_chars`.
    """

    @abstractmethod
    def run_test(
        self,
        *,
        code: str,
        langage: Langage,
        test_case: TestCase,
        limits: ExecutionLimits,
    ) -> TestRunResult:
        ...
