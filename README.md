<div align="center">

<h1>ChallengeHub</h1>

<p><strong>Plateforme de hackathons avec évaluation automatique du code et recrutement des meilleurs développeurs.</strong></p>

<p>Module AWD · Applications Web Distribuées · ESPRIT 2026-2027</p>

<p>🟣 Conception validée &nbsp;·&nbsp; 🔵 Implémentation à venir &nbsp;·&nbsp; ⚪ Déploiement à définir</p>

<p>
  <a href="#présentation">Présentation</a> ·
  <a href="#architecture">Architecture</a> ·
  <a href="#microservices">Microservices</a> ·
  <a href="#documentation">Documentation</a> ·
  <a href="#feuille-de-route">Feuille de route</a>
</p>

</div>

---

## Présentation

Une entreprise publie ses vrais problèmes techniques sous forme de défis de hackathon ; les participants proposent des solutions en Python ou Java, que la plateforme exécute et note automatiquement ; l'entreprise récupère les meilleures solutions et recrute les développeurs les mieux classés.

| 7 | 3 | 3 | 2 |
| :---: | :---: | :---: | :---: |
| microservices | frameworks back-end | types de bases | langages évalués |

> **État actuel :** la phase de conception et de modélisation (Validation 1) est terminée et documentée. Le code des services n'est pas encore implémenté.

## Architecture

![Architecture globale](documentation/architecture/global-architecture.png)

Le frontend Angular ne parle qu'à l'**API Gateway**, qui vérifie le jeton **Keycloak** (JWT), trouve le service grâce à **Eureka** et route `/api/**`. Les services lisent leur configuration dans le **Config Server** et s'appellent en REST. Chaque service possède sa propre base.

## Microservices

| # | Service | Responsabilité | Technologie | Base |
| :--- | :--- | :--- | :--- | :--- |
| MS1 | Utilisateurs (commun) | Comptes, profils, rôles, lien Keycloak | Spring Boot 3 | PostgreSQL |
| MS2 | Hackathon | Hackathons, équipes, invitations, inscriptions | Spring Boot 3 | PostgreSQL |
| MS3 | Problèmes | Énoncés, tests publics et cachés, limites, points | Spring Boot 3 | PostgreSQL |
| MS4 | Soumissions | Enregistrement, éligibilité, meilleures solutions | Spring Boot 3 | MongoDB |
| MS5 | Exécution | Exécution isolée du code, verdict par test | Python + FastAPI | MySQL |
| MS6 | Classement | Scores, rang, validation finale | NestJS | PostgreSQL |
| MS7 | Talent | Portfolio, filtre des candidats, email de recrutement | Spring Boot 3 + Mail | MongoDB |

## Workspace

| Dossier | Contenu | État |
| :--- | :--- | :--- |
| **[backend/](backend/)** | Microservices, Eureka, Config Server, Gateway | À implémenter |
| **[frontend/](frontend/)** | Application Angular | Structure de dossiers |
| **[infrastructure/](infrastructure/)** | Lancement local et déploiement | À définir |
| **[documentation/](documentation/)** | Conception, API, configuration, présentations | Complète pour la Validation 1 |

## Documentation

| Ressource | Contenu |
| :--- | :--- |
| [Index de la documentation](documentation/README.md) | Point d'entrée |
| [Cahier des charges (PDF)](documentation/specifications/cahier-des-charges.pdf) | Spécification complète |
| [Vue d'ensemble et cas d'utilisation](documentation/architecture/README.md) | Acteurs, user stories, périmètre |
| [Architecture technique](documentation/technical/architecture.md) | Microservices, technologies, risques |
| [Modèle de données](documentation/technical/data-model.md) | Diagrammes de classes par service |
| [Communication entre services](documentation/technical/communication.md) | Appels REST, parcours d'une soumission, pannes |
| [Documentation d'API](documentation/technical/api-documentation.md) | Endpoints et codes de statut |
| [Configuration](documentation/technical/configuration.md) | Ports, Eureka, Keycloak, sécurité |
| [Présentation de groupe](documentation/presentations/group-presentation.pptx) | Diaporama Validation 1 |

## Feuille de route

### 🟣 01 · Concevoir le système

- [x] Définir acteurs, cas d'utilisation et besoins fonctionnels
- [x] Découper en 7 microservices avec technologies et bases
- [x] Diagrammes de classes et architecture globale
- [x] Contrats d'API et règles de communication

### 🔵 02 · Construire l'application

- [ ] Eureka Server, Config Server, API Gateway, Keycloak
- [ ] MS1 Utilisateurs (service commun)
- [ ] MS2 à MS7, un service par étudiant
- [ ] Frontend Angular connecté à la Gateway

### 🟢 03 · Fiabiliser

- [ ] Tests de bout en bout dès que deux services communiquent
- [ ] Circuit breakers, health checks, logs
- [ ] Documentation de lancement et déploiement

## Démarrage

Il n'y a pas encore de commande de build ou de lancement. Les instructions seront ajoutées avec les premiers services ; l'ordre de démarrage prévu est décrit dans la [configuration](documentation/technical/configuration.md#lancement-local).

## Équipe

Houssein Barbirou · Youssef Ben Othmen · Mahdi Abidi · Mayssoun Miaadi · Wassim Rahli · Chedi Mastouri

## Contribuer

Gardez la documentation à côté du code. Pour tout nouveau service, décrivez sa responsabilité, son contrat d'API et sa configuration.
