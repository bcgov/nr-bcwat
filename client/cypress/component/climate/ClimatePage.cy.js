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
            .click();
        cy.get('.q-btn > span > span').contains('View More').click();
        cy.get('.chart-area').should('exist').and('be.visible');
    });
});
