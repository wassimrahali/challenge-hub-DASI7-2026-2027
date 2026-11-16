# Backend

Microservices et composants Spring Cloud de ChallengeHub. Chaque service a son propre projet, sa propre base et sa configuration.

| Composant | Technologie | Base |
| :--- | :--- | :--- |
| Eureka Server, Config Server, API Gateway | Spring Cloud | — |
| MS1 Utilisateurs (commun) | Spring Boot 3 (Java 17) | PostgreSQL |
| MS2 Hackathon | Spring Boot 3 (Java 17) | PostgreSQL |
| MS3 Problèmes | Spring Boot 3 (Java 17) | PostgreSQL |
| MS4 Soumissions | Spring Boot 3 (Java 17) | MongoDB |
| MS5 Exécution | Python + FastAPI | MySQL |
| MS6 Classement | NestJS (TypeScript) | PostgreSQL |
| MS7 Talent | Spring Boot 3 + Spring Mail | MongoDB |

Voir l'[architecture](../documentation/technical/architecture.md), le [modèle de données](../documentation/technical/data-model.md) et les [contrats d'API](../documentation/technical/api-documentation.md).
