package com.example.iobound.controller;

import com.example.iobound.dto.IoBoundResponse;
import com.example.iobound.service.IoBoundService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

import java.io.IOException;

@RestController
@RequestMapping("/io")
public class IoBoundController {
    private final IoBoundService service;

    public IoBoundController(IoBoundService service) {
        this.service = service;
    }

    @PostMapping
    public ResponseEntity<IoBoundResponse> write() {

        long start = System.nanoTime();

        try {
            service.write();

        } catch (IOException exception) {
            throw new ResponseStatusException(
                    HttpStatus.INTERNAL_SERVER_ERROR,
                    "Erro durante operação de I/O",
                    exception
            );
        }

        long end = System.nanoTime();

        double durationMs = (end - start) / 1_000_000.0;

        IoBoundResponse response =  new IoBoundResponse(
                "Operação concluída",
                durationMs,
                64L * 1024 * 1024
        );

        return ResponseEntity.ok(response);
    }
}
