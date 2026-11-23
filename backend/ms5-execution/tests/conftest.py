import os

# Avant tout import de l'application : pas d'Eureka, pas de planificateur, pas de Config Server.
os.environ["EUREKA_ENABLED"] = "false"
os.environ["SCHEDULER_ENABLED"] = "false"
os.environ["CONFIG_SERVER_URL"] = ""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings
from app.core.container import Container
from app.core.errors import NotFoundError
from app.db.base import Base
from app.db.session import get_db
from app.executor.base import CodeExecutor, TestRunResult
from app.main import app
from app.models.enums import StatutTest
from app.schemas.external import CasDeTestDTO, Langage, SoumissionDTO


class FakeMs4:
    def __init__(self):
        self.statuts: list[tuple[str, str]] = []
        self.known = {"s1", "s2", "s3"}

    async def get_soumission(self, soumission_id):
        if soumission_id not in self.known:
            raise NotFoundError("introuvable")
        return SoumissionDTO(
            id=soumission_id, code="print(1)", langage=Langage.PYTHON,
            problemeId="p1", equipeId="e1", hackathonId="h1",
        )

    async def update_statut(self, soumission_id, statut):
        self.statuts.append((soumission_id, statut.value))


class FakeMs3:
    async def get_tests(self, probleme_id):
        return [
            CasDeTestDTO(id="t1", input="1", output="1", poids=1, visible=True),
            CasDeTestDTO(id="t2", input="2", output="2", poids=3, visible=False),
        ]


class FakeMs6:
    def __init__(self):
        self.scores = []
        self.fail = False

    async def send_score(self, payload):
        if self.fail:
            raise RuntimeError("MS6 down")
        self.scores.append(payload)


class FakeExecutor(CodeExecutor):
    """Réussit le test t1 (visible), échoue le test t2 (caché)."""

    def run_test(self, *, code, langage, test_case, limits):
        if test_case.id == "t1":
            return TestRunResult(StatutTest.PASSED, 5, "1")
        return TestRunResult(StatutTest.WRONG_ANSWER, 7, "secret")


@pytest.fixture()
def env():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def override_get_db():
        session = factory()
        try:
            yield session
        finally:
            session.close()

    container = Container(
        settings=get_settings(),
        session_factory=factory,
        ms3=FakeMs3(),
        ms4=FakeMs4(),
        ms6=FakeMs6(),
        executor=FakeExecutor(),
    )
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        # Le lifespan a créé son propre conteneur : on le remplace par celui des tests.
        app.state.container = container
        yield client, container
    app.dependency_overrides.clear()
