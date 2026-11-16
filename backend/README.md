# Backend

Microservices de ChallengeHub. Chaque service possède son propre projet, sa base de données et sa configuration.

| Dossier | Service | Technologie | Base de données |
| :--- | :--- | :--- | :--- |
| `ms1-utilisateurs/` | Utilisateurs (commun) | Spring Boot 3 (Java 17) | PostgreSQL |
| `ms2-hackathon/` | Hackathon | Spring Boot 3 (Java 17) | PostgreSQL |
| `ms3-problemes/` | Problèmes | Spring Boot 3 (Java 17) | PostgreSQL |
| `ms4-soumissions/` | Soumissions | Spring Boot 3 (Java 17) | MongoDB |
| `ms5-execution/` | Exécution | Python, FastAPI | MySQL |
| `ms6-classement/` | Classement | NestJS (TypeScript) | PostgreSQL |
| `ms7-talent/` | Talent | Spring Boot 3, Spring Mail | MongoDB |

## Organisation

- Services Spring Boot : `src/main/java/tn/esprit/challengehub/<service>/` avec les paquets `entity` (ou `document` pour MongoDB), `repository`, `service`, `controller`, `dto`, `client`, `config` et `exception`.
- MS5 : paquet Python `app/` (`api`, `models`, `schemas`, `services`, `clients`, `core`, `db`).
- MS6 : sources `src/` organisées en modules NestJS (`classement`, `auth`, `health`, `clients`).

Les fichiers sont créés vides : leur contenu sera implémenté service par service.

## Références

- [Architecture technique](../documentation/technical/architecture.md)
- [Modèle de données](../documentation/technical/data-model.md)
- [Contrats d'API](../documentation/technical/api-documentation.md)
