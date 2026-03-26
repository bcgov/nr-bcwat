import { defineConfig } from "cypress";
import path from 'path';
import vitePreprocessor from 'cypress-vite'
let __dirname = '';

export default defineConfig({
  env: {
    VITE_APP_MAPBOX_TOKEN: process.env.VITE_APP_MAPBOX_TOKEN,
  },
  e2e: {
    setupNodeEvents(on, config) {
        // implement node event listeners here
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
    modifyObstructiveCode: false,
    chromeWebSecurity: false,
    testIsolation: false,
    video: true,
    videosFolder: 'cypress/videos',
    screenshotOnRunFailure: true,
    screenshotsFolder: 'cypress/screenshots',
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
      on('before:browser:launch', (browser, launchOptions) => {
        if (browser.name === 'chrome') {
            launchOptions.args.push('--ignore-gpu-blocklist')
            launchOptions.args.push('--use-gl=swiftshader')
            launchOptions.args.push('--enable-unsafe-swiftshader')
        }
        return launchOptions
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
