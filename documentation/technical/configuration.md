# Configuration

Ce document décrit la configuration cible. Les valeurs de ports et de variables sont des **propositions** à confirmer lors de l'implémentation ; les technologies, elles, sont fixées par le cahier des charges.

## Principes

- **Config Server (Spring Cloud Config)** : configuration centralisée, lue au démarrage par chaque service. MS5 (FastAPI) et MS6 (NestJS) la lisent en HTTP.
- **Eureka Server** : chaque service s'enregistre sous un nom logique en kebab-case (`hackathon-service`, `probleme-service`, `soumission-service`…).
- **Une base par service**, jamais partagée ; chaque service se lance indépendamment des autres.
- Aucun secret dans le dépôt : mots de passe, secrets de clients Keycloak et identifiants SMTP passent par variables d'environnement.

## Composants et ports proposés

| Composant | Technologie | Port proposé |
| :--- | :--- | :--- |
| Frontend | Angular | 4200 |
| API Gateway | Spring Cloud Gateway | 8080 |
| Eureka Server | Spring Cloud Netflix Eureka | 8761 |
| Config Server | Spring Cloud Config | 8888 |
| Keycloak | OAuth2 / JWT | 8180 |
| MS1 Utilisateurs | Spring Boot · PostgreSQL | 8081 |
| MS2 Hackathon | Spring Boot · PostgreSQL | 8082 |
| MS3 Problèmes | Spring Boot · PostgreSQL | 8083 |
| MS4 Soumissions | Spring Boot · MongoDB | 8084 |
| MS5 Exécution | FastAPI · MySQL | 8085 |
| MS6 Classement | NestJS · PostgreSQL | 8086 |
| MS7 Talent | Spring Boot + Mail · MongoDB | 8087 |

## Bases de données

| Service | Moteur | Contenu |
| :--- | :--- | :--- |
| MS1, MS2, MS3, MS6 | PostgreSQL | Données relationnelles |
| MS5 | MySQL | Exécutions et résultats par test |
| MS4, MS7 | MongoDB | Soumissions ; portfolios et candidatures |

Variables types : `DB_URL`, `DB_USERNAME`, `DB_PASSWORD` (ou `MONGODB_URI` pour MS4 et MS7).

## Enregistrement Eureka

Services Spring Boot :

```yaml
spring:
  application:
    name: hackathon-service
  config:
    import: "optional:configserver:http://localhost:8888"
eureka:
  client:
    service-url:
      defaultZone: http://localhost:8761/eureka
```

MS5 utilise `py-eureka-client` et MS6 `eureka-js-client`.

## Routage de la Gateway

La Gateway route `/api/**` vers le service concerné par son nom Eureka (`lb://<nom-du-service>`), après vérification du JWT. Le frontend ne contacte jamais les services directement.

## Sécurité (Keycloak)

| Élément | Valeur |
| :--- | :--- |
| Rôles | `PARTICIPANT`, `ORGANISATEUR`, `ADMIN` |
| Jetons | JWT, vérifiés par la Gateway avant chaque requête |
| Spring Boot | Spring Security (resource server) |
| MS5 | `PyJWT` |
| MS6 | `@nestjs/passport` + `passport-jwt` |
| Lien compte ↔ profil | `Utilisateur.keycloakId` (MS1) |

Variables types : `KEYCLOAK_ISSUER_URI`, `KEYCLOAK_CLIENT_ID`, `KEYCLOAK_CLIENT_SECRET`.

## Tolérance aux pannes

| Paramètre | Valeur |
| :--- | :--- |
| Circuit breaker (Spring Boot) | Resilience4j sur chaque client OpenFeign |
| Timeouts | Définis sur chaque appel inter-services |
| MS5 / MS6 | `tenacity` / `opossum` |
| Reprise des soumissions `EN_ATTENTE` | Tâche `@Scheduled` dans MS4 |
| Renvoi des scores « à transmettre » | Tâche planifiée dans MS5 |

## Exécution du code (MS5)

Le code soumis est exécuté dans un environnement isolé :

| Contrainte | Valeur |
| :--- | :--- |
| Réseau | Aucun accès |
| Mémoire | Limitée par problème (`limiteMémoireMo`) |
| CPU | Limité |
| Temps | Limité par problème (`limiteTempsMs`) |
| Utilisateur | Sans privilèges |
| Langages | Python, Java |

Plan B si l'isolation maison est trop complexe : moteur open source Judge0 piloté par FastAPI.

## Email (MS7)

Spring Mail via SMTP. Variables types : `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`. L'état du SMTP apparaît dans `/actuator/health`.

## Lancement local

Ordre recommandé : bases de données → Config Server → Eureka → Keycloak → services métier → API Gateway → frontend. Sur machine peu puissante, ne lancer que les services utiles au développement en cours.

Les commandes de build et de lancement seront ajoutées quand les premiers services seront implémentés.
