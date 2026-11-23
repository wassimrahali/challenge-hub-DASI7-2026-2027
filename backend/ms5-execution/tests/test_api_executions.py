import asyncio

from app.services.execution_service import ExecutionService


def test_flux_complet(env):
    client, container = env

    r = client.post("/api/executions", json={"soumissionId": "s1"})
    assert r.status_code == 202
    assert r.json() == {"soumissionId": "s1", "statut": "EN_ATTENTE"}

    # Les tâches de fond du TestClient sont terminées au retour de l'appel.
    r = client.get("/api/executions/s1")
    assert r.status_code == 200
    body = r.json()
    assert body["statut"] == "TERMINEE"
    assert body["verdict"] == "WRONG_ANSWER"
    assert float(body["pourcentage"]) == 25.0
    assert body["scoreTransmis"] is True
    assert len(body["resultats"]) == 2

    visible, cache = body["resultats"]
    assert visible["casDeTestId"] == "t1" and visible["sortie"] == "1"
    # Test caché : ni identifiant ni sortie exposés
    assert cache["casDeTestId"] is None and cache["sortie"] is None
    assert cache["statut"] == "WRONG_ANSWER"

    assert container.ms4.statuts == [("s1", "EXÉCUTÉE")]
    assert len(container.ms6.scores) == 1
    assert float(container.ms6.scores[0].pourcentage) == 25.0


def test_relance_ne_cree_pas_de_doublon(env):
    client, _ = env
    assert client.post("/api/executions", json={"soumissionId": "s1"}).status_code == 202
    r = client.post("/api/executions", json={"soumissionId": "s1"})
    assert r.status_code == 409
    assert r.json()["code"] == "CONFLICT"


def test_soumission_inconnue(env):
    client, _ = env
    r = client.post("/api/executions", json={"soumissionId": "inconnue"})
    assert r.status_code == 404
    assert client.get("/api/executions/inconnue").status_code == 404


def test_corps_invalide(env):
    client, _ = env
    r = client.post("/api/executions", json={})
    assert r.status_code == 400
    assert r.json()["code"] == "BAD_REQUEST"


def test_score_renvoye_si_ms6_indisponible(env):
    client, container = env
    container.ms6.fail = True

    assert client.post("/api/executions", json={"soumissionId": "s2"}).status_code == 202
    body = client.get("/api/executions/s2").json()
    assert body["statut"] == "TERMINEE"
    assert body["scoreTransmis"] is False

    # MS6 revient : la tâche planifiée renvoie le score.
    container.ms6.fail = False
    session = container.session_factory()
    try:
        sent = asyncio.run(ExecutionService(session, container).retry_pending_scores())
    finally:
        session.close()
    assert sent == 1
    assert client.get("/api/executions/s2").json()["scoreTransmis"] is True


def test_executeur_non_implemente_met_en_erreur(env):
    from app.executor.factory import NotImplementedExecutor

    client, container = env
    container.executor = NotImplementedExecutor()

    assert client.post("/api/executions", json={"soumissionId": "s3"}).status_code == 202
    body = client.get("/api/executions/s3").json()
    assert body["statut"] == "ERREUR"
    assert "pas encore implémenté" in body["messageErreur"]
    assert container.ms4.statuts == [("s3", "ERREUR")]

    # Une exécution en ERREUR peut être relancée (même ligne, pas de doublon).
    assert client.post("/api/executions", json={"soumissionId": "s3"}).status_code == 202


def test_health(env):
    client, _ = env
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "UP"
