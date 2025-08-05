describe('Streamflow page', () => {
    it('loads and renders map', () => {
        cy.visit('/streamflow');
        cy.url().should('include', 'streamflow');
        cy.get('canvas.mapboxgl-canvas').should('exist').and('be.visible');
    });

    it('shows point popup info when selected', () => {
        cy.visit('/streamflow');
        cy.url().should('include', 'streamflow');
        cy.get('.selected-point').should('not.exist');
        cy.get('.map-filter-search').type('7885')
        cy.get('.map-points-list > div > .q-item:nth-child(1)').click();
        cy.get('.selected-point').should('exist').and('be.visible');
    });

    it('loads streamflow report content', () => {
        cy.visit('/streamflow');
        cy.get('.map-filter-search').type('7885');
        cy.get('.map-points-list > div > .q-item:nth-child(1)').click();
        cy.get('.q-btn > span > span').contains('View More').click();

        // click through nav and check charts and tables exist.
        // seven day flow selected by default:
        cy.get('.report-sidebar > .q-list').children().eq(0).should('have.class', 'active');
        // flow duration tool
        cy.get('.report-sidebar > .q-list').children().eq(1).click();
        cy.get('#flow-duration-chart-container > .svg-wrap-mf > .d3-chart-mf > .g-els').should('exist');
        cy.get('#total-runoff-chart-container > .svg-wrap-fd > .d3-chart-fd > .g-els').should('exist').and('be.visible');
        cy.get('.d3-chart-tr > .g-els').should('exist')
        cy.get('.d3-chart-tr > .g-els').scrollIntoView(); // element exists, but out of viewport range (1000 x 1000)
        cy.get('.d3-chart-tr > .g-els').should('exist').and('be.visible');
        // flow metrics table
        cy.get('.report-sidebar > .q-list').children().eq(2).click();
        cy.get('.q-table > tbody').children().should('have.length.least', 1);
        // monthly mean flow table
        cy.get('.report-sidebar > .q-list').children().eq(3).click();
        cy.get('.q-table > tbody').children().should('have.length.least', 1);
        // stage chart
        cy.get('.report-sidebar > .q-list').children().eq(4).click();
        cy.get('#stage-flow-chart > #chart-container > .svg-wrap > .d3-chart > .g-els').should('exist').and('be.visible');
        cy.get('.q-btn').contains('Back to Map').click();
        cy.get('.mapboxgl-canvas').should('be.visible');
    });
});
