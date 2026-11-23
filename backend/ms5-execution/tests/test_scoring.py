from decimal import Decimal

from app.models.enums import StatutTest, Verdict
from app.services.scoring import calculer_pourcentage, determiner_verdict


def test_pourcentage_pondere():
    resultats = [(1, StatutTest.PASSED), (3, StatutTest.WRONG_ANSWER)]
    assert calculer_pourcentage(resultats) == Decimal("25.00")


def test_pourcentage_tout_reussi():
    assert calculer_pourcentage([(2, StatutTest.PASSED), (5, StatutTest.PASSED)]) == Decimal("100.00")


def test_pourcentage_arrondi_deux_decimales():
    resultats = [(1, StatutTest.PASSED), (1, StatutTest.TIMEOUT), (1, StatutTest.TIMEOUT)]
    assert calculer_pourcentage(resultats) == Decimal("33.33")


def test_pourcentage_sans_poids():
    assert calculer_pourcentage([]) == Decimal("0.00")


def test_verdict_accepte():
    assert determiner_verdict([StatutTest.PASSED, StatutTest.PASSED]) is Verdict.ACCEPTED


def test_verdict_ordre_de_gravite():
    statuts = [StatutTest.WRONG_ANSWER, StatutTest.TIMEOUT, StatutTest.RUNTIME_ERROR]
    assert determiner_verdict(statuts) is Verdict.RUNTIME_ERROR
    assert determiner_verdict([StatutTest.WRONG_ANSWER, StatutTest.TIMEOUT]) is Verdict.TIMEOUT
    assert determiner_verdict([StatutTest.PASSED, StatutTest.WRONG_ANSWER]) is Verdict.WRONG_ANSWER
    assert determiner_verdict([StatutTest.COMPILATION_ERROR, StatutTest.PASSED]) is Verdict.COMPILATION_ERROR


def test_memoire_depassee_donne_runtime_error():
    assert determiner_verdict([StatutTest.MEMORY_LIMIT]) is Verdict.RUNTIME_ERROR
