 
import { mount } from 'cypress/vue'
import { Notify, Quasar } from "quasar";
import router from "@/router";
import '@quasar/extras/material-icons/material-icons.css';
import '@quasar/extras/fontawesome-v6/fontawesome-v6.css';
import '@quasar/extras/mdi-v6/mdi-v6.css';
import 'quasar/src/css/index.sass';
import '@/main.js';

Cypress.Commands.add('mount', (component, options = {}) => {
    // skip the auth
    // Setup options object
    options.global = options.global || {}
    options.global.stubs = options.global.stubs || {}
    options.global.stubs['transition'] = false
    options.global.components = options.global.components || {}
    options.global.plugins = options.global.plugins || []

    /* Add any global plugins */
    options.global.plugins.push({
        install(app) {
            app.use(router);
            app.use(Quasar, {
                plugins: { Notify }, // import Quasar plugins and add here
            });
        },
    });
    /* Add any global components */
    // options.global.components['Button'] = Button;

    return mount(component, options)
})
