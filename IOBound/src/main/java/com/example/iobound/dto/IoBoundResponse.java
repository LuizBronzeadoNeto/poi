package com.example.iobound.dto;

public record IoBoundResponse(String message, double durationMs, long bytesWritten) {
}
