package tn.esprit.challengehub.hackathon.service;

import org.springframework.stereotype.Service;
import tn.esprit.challengehub.hackathon.dto.HackathonRequest;
import tn.esprit.challengehub.hackathon.entity.Hackathon;
import tn.esprit.challengehub.hackathon.repository.HackathonRepository;

import java.util.List;

@Service
public class HackathonService {

    private final HackathonRepository repository;

    public HackathonService(HackathonRepository repository) {
        this.repository = repository;
    }

    public Hackathon create(HackathonRequest request) {
        Hackathon hackathon = new Hackathon();
        applyRequest(hackathon, request);
        return repository.save(hackathon);
    }

    public List<Hackathon> findAll() {
        return repository.findAll();
    }

    public Hackathon findById(Long id) {
        return repository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Hackathon not found: " + id));
    }

    public Hackathon update(Long id, HackathonRequest request) {
        Hackathon hackathon = findById(id);
        applyRequest(hackathon, request);
        return repository.save(hackathon);
    }

    public void delete(Long id) {
        repository.delete(findById(id));
    }

    private void applyRequest(Hackathon hackathon, HackathonRequest request) {
        hackathon.setTitre(request.titre());
        hackathon.setDescription(request.description());
        hackathon.setOrganisateurId(request.organisateurId());
        hackathon.setDateDebut(request.dateDebut());
        hackathon.setDureeHeures(request.dureeHeures());
        hackathon.setTailleMaxEquipe(request.tailleMaxEquipe());
        hackathon.setPrix(request.prix());
    }
}
