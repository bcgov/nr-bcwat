describe('Watershed report', () => {
    it('opens when point and button are selected', () => {
        cy.visit('/watershed')
        // wait for load - temporary
        cy.wait(8000);

        // Click the first point in the list
        cy.get('.map-points-list > div:nth-child(1) > .q-item').click();

        // Validate that the watershed-lic-properties element is visible and contains content
        cy.get('[data-cy="watershed-active-point"]')
            .should('be.visible')
            .and('not.be.empty');
    });

    it('opens when watershed is selected', () => {
        cy.visit('/watershed')
        // wait for load - temporary
        cy.wait(8000);

        cy.window().then((win) => {

            console.log(win)

            const map = win.map;

            const latlng = [-127.13808593749928, 55.798511678750174]; // [lng, lat] in Mapbox
            const point = map.project(latlng);

            cy.get('.mapboxgl-canvas').click(point.x, point.y);
        });

        cy.get('[data-cy="view-report-button"]', { timeout: 10000 })
            .should('be.visible')
            .click();

        cy.get('.report-container')
            .should('have.class', 'open')
            .and('be.visible');

        cy.get('#methods').should('not.be.visible');
        cy.get('[data-cy="section-label"]').contains('Methods').click();
        cy.get('#methods').should('be.visible');
    });
});
