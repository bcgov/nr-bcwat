import { defineConfig } from 'vitest/config';

export default defineConfig({
    test: {
        globals: true,
        environment: 'jsdom', // Simulates a browser environment
        setupFiles: './vitest.setup.js', // Optional setup file
    },
});
