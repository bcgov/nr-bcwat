describe('Surface Water Quality page', () => {
    it('loads and renders map', () => {
        cy.visit('/climate');
        cy.get('canvas.mapboxgl-canvas').should('exist').and('be.visible');
        // map interaction - zoom out
        cy.wait(5000)
        cy.get('canvas.mapboxgl-canvas').type('-')
        cy.wait(1000)
        cy.get('canvas.mapboxgl-canvas').type('-')
        // when all points in BC are visible, check the listed count vs the data fixture
        const pointCount = cy.get('.map-point-count > i').text();
    });
    
    it.only('open and renders chart content', () => {
        cy.visit('/climate');
        cy.get('.q-item').first().click();
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
        cy.get('#snow-water-equivalent-chart > #chart-container > .svg-wrap > .d3-chart > .g-els').should('exist');
        // manual snow survey chart
        cy.get('.report-sidebar > .q-list').children().eq(4).click();
        cy.get('#manual-snow-survey-chart > #chart-container > .svg-wrap > .d3-chart > .g-els').should('exist');
        cy.get('.historical.line').should('not.exist');
        // open historical data dropdown
        cy.get('.yearly-input').click();
        // select first option
        cy.get('.q-item__label').contains('1997').click();
        // check chart element class now exists
        cy.get('.historical.line').should('exist');
        // clear selection
        cy.get('.q-icon[aria-label="Clear"]').click();
        cy.get('.historical.line').should('not.exist');
    });
});
