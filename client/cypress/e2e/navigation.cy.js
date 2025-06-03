describe('Navigation and routing', () => {
    it('works as expected for watershed', () => {
        cy.request('/watershed').its('status').should('eq', 200);
        cy.visit('/watershed');
        cy.get('h1').should('have.text', 'Water Allocations')
    });
    it('works as expected for streamflow', () => {
        cy.request('/streamflow').its('status').should('eq', 200);
        cy.visit('/streamflow');
        cy.get('h1').should('have.text', 'Water Allocations')
    });
    it('works as expected for surface water quality', () => {
        cy.request('/surface-water-quality').its('status').should('eq', 200);
        cy.visit('/surface-water-quality');
        cy.get('h1').should('have.text', 'Surface Water Stations')
    });
    it('works as expected for ground water quality', () => {
        cy.request('/ground-water-quality').its('status').should('eq', 200);
        cy.visit('/ground-water-quality');
        cy.get('h1').should('have.text', 'Ground Water Stations')
    });
    it('works as expected for ground water level', () => {
        cy.request('/ground-water-level').its('status').should('eq', 200);
        cy.visit('/ground-water-level');
        cy.get('h1').should('have.text', 'Ground Water Stations');
    });
    it('works as expected for climate', () => {
        cy.request('/climate').its('status').should('eq', 200);
        cy.visit('/climate');
        cy.get('h1').should('have.text', 'Climate Stations');
    });
});
