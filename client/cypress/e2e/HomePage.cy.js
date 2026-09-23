describe('HomePage', () => {
    // Clicking a link loads a map page, and its data request gets cancelled when
    // the test ends. That's expected in a link test, so ignore only that error.
    beforeEach(() => {
        cy.on('uncaught:exception', (err) => {
            if (err.name === 'AbortError') return false;
        });
        cy.visit('/');
        cy.get('.home-page-links').children().should('have.length', 11);
    });

    it('watershed link points to /watershed', () => {
        cy.get('.home-page-links > .q-item:nth-child(1)')
            .should('have.attr', 'href', '/watershed');
    });

    const clickLinks = [
        { child: 3, path: '/portal/streamflow'},
        { child: 5, path: '/portal/surface-water/quality'},
        { child: 7, path: '/portal/groundwater/quality'},
        { child: 9, path: '/portal/groundwater/level'},
        { child: 11, path: '/portal/climate'},
    ];

    clickLinks.forEach(({ child, path, header }) => {
        it(`link ${child} navigates to ${path}`, () => {
            cy.get(`.home-page-links > .q-item:nth-child(${child})`).click();
            cy.url().should('include', path);
        });
    });
});
