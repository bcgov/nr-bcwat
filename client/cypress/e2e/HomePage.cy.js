describe('HomePage', () => {
    it('links all navigate correctly', () => {
        cy.visit('/');
        cy.get('.home-page-links').children().should('have.length', 6);
        cy.get('.home-page-links > .q-item:nth-child(1)').click();
        cy.url().should('include', 'watershed');
        cy.visit('/');
        cy.get('.home-page-links > .q-item:nth-child(2)').click();
        cy.url().should('include', 'streamflow');
        cy.visit('/');
        cy.get('.home-page-links > .q-item:nth-child(3)').click();
        cy.url().should('include', 'surface-water-quality');
        cy.visit('/');
        cy.get('.home-page-links > .q-item:nth-child(4)').click();
        cy.url().should('include', 'ground-water-quality');
        cy.visit('/');
        cy.get('.home-page-links > .q-item:nth-child(5)').click();
        cy.url().should('include', 'ground-water-level');
        cy.visit('/');
        cy.get('.home-page-links > .q-item:nth-child(6)').click();
        cy.url().should('include', 'climate');
    });
});
