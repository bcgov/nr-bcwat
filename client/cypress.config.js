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
      return config
    },
    devServer: {
      framework: 'vue',
      bundler: 'vite',
    },
    baseUrl: process.env.CYPRESS_BASE_URL || "http://localhost:5173",
    fixturesFolder: 'cypress/fixtures',
    defaultCommandTimeout: 10000,
    pageLoadTimeout: 60000,
    chromeWebSecurity: false,
    testIsolation: false,
  },
  component: {
    setupNodeEvents(on, config) {
      // include any other plugin code...
      on('task', {
          log (message) {
              console.log(message)
              return null
          }
      })
      // It's IMPORTANT to return the config object
      // with any changed environment variables
      return config
    },
    viewportHeight: 1000,
    viewportWidth: 1000,
    devServer: {
      framework: 'vue',
      bundler: 'vite',
    },
    fixturesFolder: 'cypress/fixtures',
    retries: 1,
    defaultCommandTimeout: 10000,
    video: false,
    screenshotOnRunFailure: false,
  },
  env: {
    server_url: process.env.VITE_BASE_API_URL,
  },
});
