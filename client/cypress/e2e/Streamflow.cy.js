describe('Streamflow page', () => {
    it('loads and renders map', () => {
        cy.visit('/streamflow');
        cy.get('.q-list > .q-item').first().click();
        cy.get('.q-btn > span > span').contains('View More').click();
    });
});
