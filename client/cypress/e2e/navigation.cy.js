describe('Navigation and routing', () => {
    it('works as expected for watershed', () => {
        cy.visit('/watershed');
        cy.get('.map-filters-header').should('have.text', 'Water Allocations')
    });
    it('works as expected for streamflow', () => {
        cy.visit('/streamflow');
        cy.get('.map-filters-header').should('have.text', 'Streamflow Gauges')
    });
    it('works as expected for surface water quality', () => {
        cy.visit('/surface-water-quality');
        cy.get('.map-filters-header').should('have.text', 'Water Quality Stations')
    });
    it('works as expected for ground water quality', () => {
        cy.visit('/ground-water-quality');
        cy.get('.map-filters-header').should('have.text', 'Ground Water Quality')
    });
    it('works as expected for ground water level', () => {
        cy.visit('/ground-water-level');
        cy.get('.map-filters-header').should('have.text', 'Observation Wells');
    });
    it('works as expected for climate', () => {
        cy.visit('/climate');
        cy.get('.map-filters-header').should('have.text', 'Weather Stations');
    });
});
