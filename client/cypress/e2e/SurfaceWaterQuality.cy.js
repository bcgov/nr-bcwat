describe('Surface Water Quality page', () => {
    it('loads and renders map', () => {
        cy.visit('/surface-water-quality');
        cy.get('canvas.mapboxgl-canvas').should('exist').and('be.visible');
        // map interaction - zoom out
    });

    it('open and renders chart content', () => {
        cy.visit('/surface-water-quality');
        cy.get('.map-filter-search').type('47249')
        cy.get('.map-points-list > div > .q-item:nth-child(1)').click();
        cy.get('.q-btn > span > span').contains('View More').click();
        cy.get('.report-container').should('have.class', 'open');
        cy.get('.report-sidebar > .q-list').children().should('have.length', 1);
        cy.get('.report-sidebar > .q-list > .q-item').should('have.class', 'active');
        cy.get('.report-sidebar > .q-list > .q-item > div.text-h6').should('contain', 'Surface Water Quality');

        // check that the correct number of charts are displayed.
        cy.get('.water-quality-table > tbody').children().should('have.length.least', 1);

        // closes report
        cy.get('.q-btn').contains('Back to Map').click();
        cy.get('.report-container').should('not.have.class', 'open');
        cy.get('canvas.mapboxgl-canvas').should('exist').and('be.visible');
    });
});
