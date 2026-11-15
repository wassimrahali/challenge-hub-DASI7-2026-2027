# Documentation — ChallengeHub

ChallengeHub est une plateforme de hackathons avec évaluation automatique du code et recrutement des meilleurs développeurs (module AWD — ESPRIT 2026-2027). Une entreprise publie ses vrais problèmes techniques sous forme de défis ; les participants soumettent du code Python ou Java, exécuté et noté automatiquement ; l'entreprise récupère les meilleures solutions et recrute les développeurs les mieux classés.

## Index

| Document | Contenu |
| :--- | :--- |
| [Cahier des charges (PDF)](specifications/cahier-des-charges.pdf) | Spécification complète de la Validation 1 |
| [Présentation du groupe](presentations/group-presentation.pptx) | Diaporama de la Validation 1 |
| [Vue d'ensemble et acteurs](architecture/README.md) | Contexte, acteurs, cas d'utilisation, besoins fonctionnels |
| [Architecture technique](technical/architecture.md) | Microservices, technologies, infrastructure Spring Cloud |
| [Modèle de données](technical/data-model.md) | Classes et énumérations de chaque microservice |
| [Communication entre services](technical/communication.md) | Appels REST, parcours d'une soumission, gestion des pannes |
| [Documentation d'API](technical/api-documentation.md) | Endpoints, codes de statut, supervision |
| [Configuration](technical/configuration.md) | Ports, Config Server, Eureka, Keycloak, sécurité |

## Diagrammes

| Diagramme | Fichier |
| :--- | :--- |
| Cas d'utilisation | [use-case-diagram.png](architecture/use-case-diagram.png) |
| Architecture globale | [global-architecture.png](architecture/global-architecture.png) |
| MS1 Utilisateurs | [ms1-class-diagram.png](architecture/class-diagrams/ms1-class-diagram.png) |
| MS2 Hackathon | [ms2-class-diagram.png](architecture/class-diagrams/ms2-class-diagram.png) |
| MS3 Problèmes | [ms3-class-diagram.png](architecture/class-diagrams/ms3-class-diagram.png) |
| MS4 Soumissions | [ms4-class-diagram.png](architecture/class-diagrams/ms4-class-diagram.png) |
| MS5 Exécution | [ms5-class-diagram.png](architecture/class-diagrams/ms5-class-diagram.png) |
| MS6 Classement | [ms6-class-diagram.png](architecture/class-diagrams/ms6-class-diagram.png) |
| MS7 Talent | [ms7-class-diagram.png](architecture/class-diagrams/ms7-class-diagram.png) |

## Équipe

Houssein Barbirou · Youssef Ben Othmen · Mahdi Abidi · Mayssoun Miaadi · Wassim Rahli · Chedi Mastouri
