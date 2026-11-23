"""Calcul du pourcentage et du verdict global (fonctions pures)."""
from decimal import ROUND_HALF_UP, Decimal
from typing import Iterable

from app.models.enums import StatutTest, Verdict

# Du plus grave au moins grave : le verdict global est le premier présent dans les résultats.
_GRAVITE: list[tuple[StatutTest, Verdict]] = [
    (StatutTest.COMPILATION_ERROR, Verdict.COMPILATION_ERROR),
    (StatutTest.RUNTIME_ERROR, Verdict.RUNTIME_ERROR),
    (StatutTest.MEMORY_LIMIT, Verdict.RUNTIME_ERROR),
    (StatutTest.TIMEOUT, Verdict.TIMEOUT),
    (StatutTest.WRONG_ANSWER, Verdict.WRONG_ANSWER),
]


def calculer_pourcentage(resultats: Iterable[tuple[int, StatutTest]]) -> Decimal:
    """Somme des poids des tests réussis / somme des poids x 100 (2 décimales)."""
    total = 0
    reussi = 0
    for poids, statut in resultats:
        total += poids
        if statut is StatutTest.PASSED:
            reussi += poids
    if total <= 0:
        return Decimal("0.00")
    return (Decimal(reussi) * 100 / Decimal(total)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )


def determiner_verdict(statuts: Iterable[StatutTest]) -> Verdict:
    presents = set(statuts)
    for statut, verdict in _GRAVITE:
        if statut in presents:
            return verdict
    return Verdict.ACCEPTED
