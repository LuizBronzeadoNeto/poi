package com.example.iobound.service;

import org.springframework.stereotype.Service;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.Random;

@Service
public class IoBoundService {

    private static final int BLOCK_SIZE = 1024 * 1024;
    private static final int BLOCK_COUNT = 64;

    private static final byte[] data = new byte[BLOCK_SIZE];

    private final Path directory = Path.of("files");

    public IoBoundService() throws IOException {
        Files.createDirectories(directory);
    }

    static {
        new Random(100).nextBytes(data);
    }

    public void write() throws IOException {

        Path file = Files.createTempFile(
                directory,
                "file-",
                ".txt"
        );

        try {
            try (FileChannel channel = FileChannel.open(
                    file,
                    StandardOpenOption.WRITE)) {

                ByteBuffer buffer = ByteBuffer.wrap(data);

                for (int i = 0; i < BLOCK_COUNT; i++) {
                    buffer.rewind();

                    while (buffer.hasRemaining()) {
                        channel.write(buffer);
                    }

                    channel.force(true);
                }

            }

        } finally {
            Files.deleteIfExists(file);
        }
    }


}
