describe('Surface Water Quality page', () => {
    it('loads and renders map', () => {
        cy.visit('/climate');
        cy.get('canvas.mapboxgl-canvas').should('exist').and('be.visible');
    });

    it('open and renders chart content', () => {
        cy.visit('/climate');
        cy.get('.map-filter-search').type('47521')
        cy.get('.map-points-list > div > .q-item:nth-child(1)').click();
        cy.get('.q-btn > span > span').contains('View More').click();
        cy.get('.report-container').should('have.class', 'open');
        cy.get('.report-sidebar > .q-list').children().should('have.length', 5);
        cy.get('.report-sidebar > .q-list > .q-item').first().should('have.class', 'active');

        // Temperature chart
        cy.get('#temperature-chart > #chart-container > .svg-wrap > .d3-chart > .g-els').should('exist');
        // Precipitation chart
        cy.get('.report-sidebar > .q-list').children().eq(1).click();
        cy.get('#precipitation-chart > #chart-container > .svg-wrap > .d3-chart > .g-els').should('exist');
        // snow on ground chart
        cy.get('.report-sidebar > .q-list').children().eq(2).click();
        cy.get('#snow-on-ground-chart > #chart-container > .svg-wrap > .d3-chart > .g-els').should('exist');
        // snow water equivalent chart
        cy.get('.report-sidebar > .q-list').children().eq(3).click();
        cy.get('.historical.line').should('not.exist');
        // manual snow survey chart
        cy.get('.report-sidebar > .q-list').children().eq(4).click();
        cy.get('.historical.line').should('not.exist');
    });

    it('successfully searches', () => {
        cy.visit('/climate')
        cy.get('[data-cy="search-type"]').click();
        cy.get('span').contains('Place Name').click();
        cy.get('.search-input').type('Williams');
        cy.get('.search-results-container > .search-result:nth-child(1)').click();
    });
});
