package tn.esprit.challengehub.hackathon.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import tn.esprit.challengehub.hackathon.entity.Hackathon;

public interface HackathonRepository extends JpaRepository<Hackathon, Long> {
}
