from app.executor.base import CodeExecutor, ExecutionLimits, TestCase, TestRunResult
from app.schemas.external import Langage


class NotImplementedExecutor(CodeExecutor):
    """Exécuteur provisoire : toute exécution échoue avec un message explicite.

    Remplacé par l'exécuteur à sous-processus isolé à l'étape 2.
    """

    def run_test(
        self,
        *,
        code: str,
        langage: Langage,
        test_case: TestCase,
        limits: ExecutionLimits,
    ) -> TestRunResult:
        raise NotImplementedError("L'exécuteur de code n'est pas encore implémenté")


def create_executor() -> CodeExecutor:
    return NotImplementedExecutor()
