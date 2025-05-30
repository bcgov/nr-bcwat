import groundwaterLevelStations from '@/constants/groundWaterLevelStations'

const count = groundwaterLevelStations.features.length;

describe('Groundwater Level page', () => {
    it('loads and renders map', () => {
        cy.visit('/ground-water-level');
        cy.get('canvas.mapboxgl-canvas').should('exist').and('be.visible');
        // map interaction - zoom out
        cy.wait(5000)
        cy.get('canvas.mapboxgl-canvas').type('-')
        cy.wait(1000)
        cy.get('canvas.mapboxgl-canvas').type('-')
        // when all points in BC are visible, check the listed count vs the data fixture
        cy.get('.map-point-count > i').contains(count);
    });
    it('opens popup and chart', () => {
        cy.visit('/ground-water-level');
        cy.get('.selected-point').should('not.exist');
        cy.get('.q-item').first().click();
        cy.get('.selected-point').should('exist').and('be.visible');
        cy.get('.q-btn > span > span').contains('View More').click();
        // ensure the report pop-open has been opened
        cy.get('.report-sidebar > .q-list').children().eq(0).should('have.class', 'active');
        // chart is rendered
        cy.get('.d3-chart > .g-els').should('exist').and('be.visible');
    })
});
