package tn.esprit.challengehub.hackathon.controller;

import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;
import tn.esprit.challengehub.hackathon.dto.HackathonRequest;
import tn.esprit.challengehub.hackathon.entity.Hackathon;
import tn.esprit.challengehub.hackathon.service.HackathonService;

import java.util.List;

@RestController
@RequestMapping("/api/hackathons")
public class HackathonController {

    private final HackathonService service;

    public HackathonController(HackathonService service) {
        this.service = service;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public Hackathon create(@Valid @RequestBody HackathonRequest request) {
        return service.create(request);
    }

    @GetMapping
    public List<Hackathon> findAll() {
        return service.findAll();
    }

    @GetMapping("/{id}")
    public Hackathon findById(@PathVariable Long id) {
        return service.findById(id);
    }

    @PutMapping("/{id}")
    public Hackathon update(@PathVariable Long id,
                           @Valid @RequestBody HackathonRequest request) {
        return service.update(id, request);
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void delete(@PathVariable Long id) {
        service.delete(id);
    }
}
