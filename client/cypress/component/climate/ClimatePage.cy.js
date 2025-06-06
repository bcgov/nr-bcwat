import ClimatePage from "@/components/climate/ClimatePage.vue";

describe('<ClimatePage />', () => {
    it('mounts and renders components', () => {
        cy.mount(ClimatePage);
        cy.get('.search-entry').should('exist');
        cy.get('.map-filters-container').should('exist');
    });
    it('opens report', () => {
        cy.mount(ClimatePage);
        cy.get('.q-virtual-scroll__content')
            .children()
            .first()
            .click({ force: true });
        cy.wait(1000);
        cy.get('.q-btn > span > span').contains('View More').click();
        cy.wait(500);
        cy.get('.chart-area').should('exist').and('be.visible');
    });
});
