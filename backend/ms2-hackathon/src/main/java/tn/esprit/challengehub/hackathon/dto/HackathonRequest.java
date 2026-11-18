package tn.esprit.challengehub.hackathon.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public record HackathonRequest(
        @NotBlank String titre,
        String description,
        @NotNull Long organisateurId,
        String dateDebut,
        Integer dureeHeures,
        Integer tailleMaxEquipe,
        Double prix
) {}
