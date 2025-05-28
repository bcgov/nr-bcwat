import { fileURLToPath, URL } from "node:url";
import { quasar, transformAssetUrls } from "@quasar/vite-plugin";
import { defineConfig, loadEnv } from "vite";
import vue from "@vitejs/plugin-vue";

// https://vite.dev/config/
export default ({ mode }) => {
  // Load VITE_* vars from .env files into process.env
  loadEnv(mode, process.cwd(), "");

  return defineConfig({
    plugins: [
      vue({
        template: {
          transformAssetUrls,
        },
      }),
      quasar({
        sassVariables: "@/assets/quasar-variables.sass",
      }),
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
  });
};
