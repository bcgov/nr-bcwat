describe('Navigation and routing', () => {
    it('works as expected for watershed', () => {
        cy.visit('/watershed');
        cy.get('h1').should('have.text', 'Water Allocations')
    });
    it('works as expected for streamflow', () => {
        cy.visit('/streamflow');
        cy.get('h1').should('have.text', 'Water Allocations')
    });
    it('works as expected for surface water quality', () => {
        cy.visit('/surface-water-quality');
        cy.get('h1').should('have.text', 'Surface Water Stations')
    });
    it('works as expected for ground water quality', () => {
        cy.visit('/ground-water-quality');
        cy.get('h1').should('have.text', 'Ground Water Stations')
    });
    it('works as expected for ground water level', () => {
        cy.visit('/ground-water-level');
        cy.get('h1').should('have.text', 'Ground Water Stations');
    });
    it('works as expected for climate', () => {
        cy.visit('/climate');
        cy.get('h1').should('have.text', 'Climate Stations');
    });
});
