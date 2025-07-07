import ClimatePage from "@/components/climate/ClimatePage.vue";

describe('<ClimatePage />', () => {
    beforeEach(() => {
        cy.intercept('/climate/stations', { fixture: 'climateStations.json' });
    });

    it('mounts and renders components', () => {
        cy.mount(ClimatePage);
        cy.get('.search-entry').should('exist');
        cy.get('.map-filters-container').should('exist');
    });
    it('opens report', () => {
        cy.mount(ClimatePage);
        cy.get('.map-points-list')
            .children()
            .first()
            .click();
        cy.get('.q-btn > span > span').contains('View More').click();
        cy.get('.chart-area').should('exist').and('be.visible');

        // closes report
        cy.get('.block').contains('Back to Map').click();
        cy.get('.chart-area').should('exist').and('not.be.visible');
    });
});
