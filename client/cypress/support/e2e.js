// ***********************************************************
// This example support/e2e.js is processed and
// loaded automatically before your test files.
//
// This is a great place to put global configuration and
// behavior that modifies Cypress.
//
// You can change the location of this file or turn off
// automatically serving support files with the
// 'supportFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/configuration
// ***********************************************************

// Import commands.js using ES2015 syntax:
import './commands'

Cypress.Commands.add('waitForAppReady', () => {
    cy.window().its('vueAppReady').should('be.true');
});

Cypress.on('uncaught:exception', (err) => {
    // requests cancelled by navigating away are expected; ignore only those
    if (err.name === 'AbortError' || err.message.includes('The operation was aborted')) {
        return false;
    }
    // any other application error still fails the test
});
