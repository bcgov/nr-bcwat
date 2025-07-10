import ClimatePage from "@/components/climate/ClimatePage.vue";

describe('<ClimatePage />', () => {
    beforeEach(() => {
        cy.intercept('/climate/stations', { fixture: 'climateStations.json' });
        cy.intercept('/climate/**/report', { fixture: 'climateReport.json' });
    });

    it('mounts and renders components', () => {
        cy.mount(ClimatePage);
        cy.get('.search-entry').should('exist');
        cy.get('.map-filters-container').should('exist');
    });
    it('opens report', () => {
        cy.mount(ClimatePage);
        cy.wait(1000);
        cy.get('.map-points-list > .q-virtual-scroll__content')
            .children()
            .first()
            .click();
        cy.wait(1000);
        cy.get('.q-btn > span > span').contains('View More').click();
        cy.wait(1000);
        cy.get('.chart-area').should('exist').and('be.visible');

        // closes report
        cy.get('[data-cy="back-to-map"]').click();
        cy.get('.chart-area').should('not.exist');
    });
});
