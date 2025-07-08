describe('Watershed report', () => {
    it('opens when point and button are selected', () => {
        cy.visit('/watershed')
        // wait for load - temporary
        cy.wait(8000);
        cy.get('.mapboxgl-canvas').click();
        cy.get('[data-cy="report-btn"]').click();
        cy.get('.report-container').should('have.class', 'open').and('be.visible');
        cy.get('#methods').should('not.be.visible');
        cy.get('.q-item__section > b').contains('Methods').click();
        cy.get('#methods').should('be.visible');
    });
    it('renders maps and charts', () => {
        // this is very simple - can be expanded to check more sections as desired
        cy.get('.q-item__section > b').contains('Annual Hydrology').click();
        cy.get('#hydrologyMapContainer').scrollIntoView();
        cy.get('#hydrologyMapContainer > .mapboxgl-canvas-container').should('be.visible');
        cy.wait(200)
        cy.get('.q-item__section > b').contains('Monthly Hydrology').click();
        cy.get('#monthly-chart > svg > g').scrollIntoView();
        cy.get('#monthly-chart > svg > g').should('exist').and('be.visible');
        cy.get('#monthly-chart-downstream > svg > g').scrollIntoView();
        cy.get('#monthly-chart-downstream > svg > g').should('exist').and('be.visible');
        cy.get('.q-item__section > b').contains('Hydrologic Variability').click();
        cy.get('#hydrologicVariabilityMapContainer').scrollIntoView();
        cy.get('.mapboxgl-canvas-container').should('exist').and('be.visible');
    });
});
