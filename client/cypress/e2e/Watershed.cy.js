describe('Watershed report', () => {
    it('opens when point and button are selected', () => {
        cy.visit('/watershed')
        // wait for load - temporary
        cy.wait(8000);
        cy.get('.map-points-list').children().first().click();
        cy.get('.search-result').click();
        cy.get('[data-cy="view-report-button"]').click();
        cy.get('.report-container').should('have.class', 'open').and('be.visible');
        cy.get('#methods').should('not.be.visible');
        cy.get('[data-cy="section-label"]').contains('Methods').click();
        cy.get('#methods').should('be.visible');
    });
});
