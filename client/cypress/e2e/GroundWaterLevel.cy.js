describe('Groundwater Level page', () => {
    it('loads and renders map', () => {
        cy.visit('/ground-water-level');
        cy.get('canvas.mapboxgl-canvas').should('exist').and('be.visible');
    });
    it('opens popup, chart, and table', () => {
        cy.visit('/ground-water-level');
        cy.get('.selected-point').should('not.exist');
        cy.get('.map-filter-search').type('16845');
        cy.get('.map-points-list > div > .q-item:nth-child(1)').click();
        cy.get('.selected-point').should('exist').and('be.visible');
        cy.get('.q-btn > span > span').contains('View More').click();
        // ensure the report pop-open has been opened
        cy.get('.report-sidebar > .q-list').children().eq(0).should('have.class', 'active');
        // chart is rendered
        cy.get('.d3-chart > .g-els').should('exist').and('be.visible');
        // Monthly mean levels
        cy.get('.report-sidebar > .q-list').children().eq(1).click();
        cy.get('.q-table__container').should('be.visible');
    })
});
