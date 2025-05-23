import { defineConfig } from 'vitest/config';
import { fileURLToPath, URL } from "node:url";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
    plugins: [
        vue()
    ],
    resolve: {
        alias: {
            "@": fileURLToPath(new URL("./src", import.meta.url)),
        },
    },
    test: {
        globals: true,
        css: true,
        deps: {
            web: {
                transformCss: true,
            }
        },
        dir: './testing/vitest',
        environment: 'jsdom', // Simulates a browser environment
    },
});
