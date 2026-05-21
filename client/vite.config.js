import { fileURLToPath, URL } from "node:url";
import { quasar, transformAssetUrls } from "@quasar/vite-plugin";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import Sitemap from 'vite-plugin-sitemap';
import { routePaths } from "./src/utils/constants";
import { buildEnv } from "./src/buildEnv";
import sri from "vite-plugin-sri-gen";

// https://vite.dev/config/
export default defineConfig(({ command, mode, isSsrBuild, isPreview }) => {
    return {
        plugins: [
            vue({
                template: {
                    transformAssetUrls,
                },
            }),
            quasar({
                sassVariables: "@/assets/quasar-variables.sass",
            }),
            // Automatically creates a sitemap.xml and robots.txt files from the routes in the vue-router
            Sitemap({
                dynamicRoutes: routePaths,
                hostname : buildEnv.CLIENT_URL
            }),
            // Automatically creates sri with unique identifier sha's for script src's in index.html
            // Resolves ZAP security vulnerability - Insufficient Site Isolation Against Spectre Vulnerability
            sri({
                algorithm: "sha384", // 'sha256' | 'sha384' | 'sha512' (default: 'sha384')
                crossorigin: "anonymous", // 'anonymous' | 'use-credentials' | undefined
                fetchCache: true, // cache remote fetches in-memory and dedupe concurrent requests (default: true)
                fetchTimeoutMs: 5000, // abort remote fetches after N ms; 0 disables timeout (default: 5000)
                skipResources: [], // skip SRI for resources matching these patterns (default: [])
            })
        ],
        resolve: {
            alias: {
                "@": fileURLToPath(new URL("./src", import.meta.url)),
            },
        },
        css: {
            preprocessorOptions: {
                scss: {
                    additionalData: `@import "@/assets/main.scss";`,
                    api: "modern-compiler",
                },
            },
        },
        // Only Impacts Dev Environment - helps with unit testing.
        // https://vite.dev/config/server-options#server-proxy
        server: {
            proxy: {
                '/api': {
                    target: 'http://localhost:8000',
                    changeOrigin: true,
                    rewrite: path => path.replace(/^\/api/, '')
                }
            }
        }
    }
});
