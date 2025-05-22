import { defineConfig } from "cypress";
import path from 'path';
import vitePreprocessor from 'cypress-vite'
let __dirname = '';

export default defineConfig({
  e2e: {
    setupNodeEvents(on, config) {
      // implement node event listeners here
      on(
        'file:preprocessor',
        vitePreprocessor({
          configFile: path.resolve(__dirname, './vite.config.js'),
          mode: 'development',
        }),
      )
    },
        devServer: {
            framework: 'vue',
            bundler: 'vite',
        },
        baseUrl: "http://localhost:5173",
        fixturesFolder: 'cypress/fixtures',
        defaultCommandTimeout: 10000,
        chromeWebSecurity: false,
        testIsolation: false,
  },
});
