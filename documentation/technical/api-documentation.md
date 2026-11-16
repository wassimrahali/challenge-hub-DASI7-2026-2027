# Documentation d'API

Chaque service documente son API : `springdoc-openapi` (Swagger UI sur `/swagger-ui.html`) pour Spring Boot, `/docs` pour FastAPI (MS5), `@nestjs/swagger` pour NestJS (MS6).

## Conventions

- Le frontend n'appelle que l'**API Gateway**, qui route `/api/**` vers le bon service via Eureka.
- Authentification : en-tête `Authorization: Bearer <JWT Keycloak>`, vérifié par la Gateway avant chaque requête.
- Rôles : `PARTICIPANT`, `ORGANISATEUR`, `ADMIN`.
- Les endpoints marqués *interne* ne sont appelés que par d'autres services.
- Codes : `200` OK · `201` créé · `202` accepté (traitement asynchrone) · `400` requête invalide · `403` interdit · `404` introuvable · `409` conflit d'état · `503` service dépendant indisponible.

## Endpoints

### MS1 — Utilisateurs

| Méthode et URI | Rôle | Codes |
| :--- | :--- | :--- |
| `POST /api/utilisateurs/inscription` | Créer un compte | 201, 400, 409 |
| `GET /api/utilisateurs/{id}` | Profil d'un utilisateur (appelé par tous les services) | 200, 404 |
| `PATCH /api/entreprises/{id}/validation` | Valider une entreprise (admin) | 200, 403, 404 |

### MS2 — Hackathon

| Méthode et URI | Rôle | Codes |
| :--- | :--- | :--- |
| `POST /api/hackathons` | Créer un hackathon | 201, 400, 403 |
| `GET /api/hackathons/{id}` | Détail d'un hackathon | 200, 404 |
| `PATCH /api/hackathons/{id}/statut` | Ouvrir, lancer, clôturer | 200, 409 |
| `POST /api/equipes` | Créer une équipe | 201, 400 |
| `POST /api/equipes/{id}/invitations` | Inviter un membre | 201, 404, 409 |
| `POST /api/inscriptions` | Inscrire l'équipe au hackathon | 201, 403, 409 |
| `GET /api/inscriptions?equipeId=` | Inscription d'une équipe (interne) | 200 |

### MS3 — Problèmes

| Méthode et URI | Rôle | Codes |
| :--- | :--- | :--- |
| `POST /api/problemes` | Créer un problème | 201, 400, 403 |
| `POST /api/problemes/{id}/tests` | Ajouter un test (input, output, poids) | 201, 400 |
| `GET /api/problemes/{id}` | Énoncé, sans les tests cachés | 200, 404 |
| `GET /api/problemes/{id}/tests` | Tous les tests (interne, MS5) | 200, 404 |

### MS4 — Soumissions

| Méthode et URI | Rôle | Codes |
| :--- | :--- | :--- |
| `POST /api/soumissions` | Enregistrer une soumission | 202, 400, 403, 409, 503 |
| `GET /api/soumissions/{id}` | Statut d'une soumission | 200, 403, 404 |
| `GET /api/soumissions/meilleures?problemeId=` | Code des meilleures solutions (organisateur du hackathon) | 200, 403 |
| `PATCH /api/soumissions/{id}/statut` | Changer le statut (interne, MS5) | 200, 404 |

### MS5 — Exécution

| Méthode et URI | Rôle | Codes |
| :--- | :--- | :--- |
| `POST /api/executions` | Lancer l'exécution d'une soumission (interne, MS4) | 202, 404, 409 |
| `GET /api/executions/{soumissionId}` | Verdict, pourcentage, résultat par test | 200, 403, 404 |
| `GET /api/executions/meilleures?problemeId=` | Meilleurs résultats | 200 |

### MS6 — Classement

| Méthode et URI | Rôle | Codes |
| :--- | :--- | :--- |
| `POST /api/classements/scores` | Recevoir un score (interne, MS5) | 200, 400 |
| `GET /api/classements/{hackathonId}` | Classement | 200, 404 |
| `GET /api/classements/{hackathonId}/resolveurs?problemeId=` | Équipes ayant résolu un problème à 100 % | 200, 404 |
| `POST /api/classements/{hackathonId}/validation` | Valider les résultats finaux (organisateur) | 200, 403, 409 |

### MS7 — Talent

| Méthode et URI | Rôle | Codes |
| :--- | :--- | :--- |
| `GET /api/portfolios/{userId}` | Portfolio d'un participant | 200, 403, 404 |
| `PATCH /api/portfolios/{userId}/visibilite` | Visible ou non par les recruteurs | 200 |
| `POST /api/portfolios/participations` | Recevoir les résultats validés (interne, MS6) | 200 |
| `GET /api/recrutements/candidats?hackathonId=&top=` | Candidats filtrés (top N, ou `problemeResolu=`) | 200, 403 |
| `POST /api/recrutements` | Présélectionner un candidat et envoyer l'email | 201, 403, 409 |

### Précisions sur les codes d'erreur

- `POST /api/recrutements` → **403** si le candidat n'a pas rendu son portfolio visible ; **409** s'il est déjà présélectionné pour ce hackathon.
- `GET /api/soumissions/meilleures` → **403** : seul l'organisateur de ce hackathon voit le code.
- `POST /api/soumissions` → **409** hackathon non en cours ; **403** équipe non inscrite ; **503** MS2 indisponible.

## Visibilité des tests

`GET /api/problemes/{id}` ne renvoie jamais les tests cachés (`visible = false`). Ils ne sont lisibles que par MS5 via l'endpoint interne. Le détail par test d'une exécution est masqué pour les tests cachés.

## Supervision

Chaque service Spring Boot (MS1, MS2, MS3, MS4, MS7) active Actuator :

| Endpoint | Ce qu'il montre |
| :--- | :--- |
| `/actuator/health` | État UP / DOWN du service et de ses dépendances (base, SMTP pour MS7) |
| `/actuator/info` | Nom, version, description |
| `/actuator/metrics` | Requêtes HTTP, mémoire, temps de réponse |

MS5 (FastAPI) et MS6 (NestJS, module Terminus) exposent un `/health` équivalent. MS7 ajoute un indicateur de santé SMTP.

## Versionnement

Les contrats Swagger sont fixés tôt entre les équipes et partagés avec des exemples d'appels. Les URI sont préfixées par `/api` ; aucune version dans l'URI à ce stade.
