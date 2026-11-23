"""DTO des services appelés (MS3, MS4, MS6).

Les noms de champs JSON sont ceux supposés dans documentation/technical/api-documentation.md ;
`extra="ignore"` rend la lecture tolérante. À ajuster avec les équipes MS3 et MS4 si besoin.
"""
import enum
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class Langage(str, enum.Enum):
    PYTHON = "PYTHON"
    JAVA = "JAVA"


class StatutSoumission(str, enum.Enum):
    EXECUTEE = "EXÉCUTÉE"
    ERREUR = "ERREUR"


class _External(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")


class SoumissionDTO(_External):
    """GET MS4 /api/soumissions/{id}"""

    id: str
    code: str
    langage: Langage
    probleme_id: str = Field(alias="problemeId")
    equipe_id: str = Field(alias="equipeId")
    hackathon_id: str = Field(alias="hackathonId")


class CasDeTestDTO(_External):
    """Élément de GET MS3 /api/problemes/{id}/tests"""

    id: str
    input: str = ""
    output: str = ""
    poids: int = 1
    visible: bool = True
    temps_limite_ms: int | None = Field(default=None, alias="tempsLimiteMs")
    memoire_limite_mb: int | None = Field(default=None, alias="memoireLimiteMb")


class StatutUpdate(BaseModel):
    """Corps de PATCH MS4 /api/soumissions/{id}/statut"""

    statut: StatutSoumission


class ScorePayload(BaseModel):
    """Corps de POST MS6 /api/classements/scores"""

    model_config = ConfigDict(populate_by_name=True)

    hackathon_id: str = Field(alias="hackathonId")
    equipe_id: str = Field(alias="equipeId")
    probleme_id: str = Field(alias="problemeId")
    soumission_id: str = Field(alias="soumissionId")
    pourcentage: Decimal
