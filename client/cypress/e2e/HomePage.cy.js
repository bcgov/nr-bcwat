describe('HomePage', () => {
    it('links all navigate correctly', () => {
        cy.visit('/');
        cy.wait(5000);
        cy.get('.home-page-links').children().should('have.length', 11);
        cy.get('.home-page-links > .q-item:nth-child(1)').click();
        cy.url().should('include', 'watershed');
        cy.get('.loader-container', { timeout: 30000 }).should('not.exist');
        cy.visit('/');
        cy.wait(5000);
        cy.get('.home-page-links > .q-item:nth-child(3)').click();
        cy.url().should('include', 'streamflow');
        cy.get('.loader-container', { timeout: 30000 }).should('not.exist');
        cy.visit('/');
        cy.wait(5000);
        cy.get('.home-page-links > .q-item:nth-child(5)').click();
        cy.url().should('include', 'surface-water');
        cy.get('.loader-container', { timeout: 30000 }).should('not.exist');
        cy.visit('/');
        cy.wait(5000)
        cy.get('.home-page-links > .q-item:nth-child(7)').click();
        cy.url().should('include', 'groundwater/quality');
        cy.get('.loader-container', { timeout: 30000 }).should('not.exist');
        cy.visit('/');
        cy.get('.home-page-links > .q-item:nth-child(9)').click();
        cy.url().should('include', 'groundwater/level');
        cy.get('.loader-container', { timeout: 30000 }).should('not.exist');
        cy.visit('/');
        cy.get('.home-page-links > .q-item:nth-child(11)').click();
        cy.url().should('include', 'portal/climate');
        cy.get('.loader-container', { timeout: 30000 }).should('not.exist');
    });
});
