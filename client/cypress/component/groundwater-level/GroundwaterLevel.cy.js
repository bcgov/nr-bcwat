import GroundwaterLevel from "@/components/groundwater-level/GroundwaterLevel.vue";
import groundWaterLevelStations from '@/constants/groundWaterLevelStations.json';

const pointCount = groundWaterLevelStations.features.length;

describe('<GroundwaterLevel />', () => {
    it('mounts and renders the map', () => {
        cy.mount(GroundwaterLevel);
        cy.get('.mapboxgl-canvas').should('exist').and('be.visible');
        // zoom out of the map, showing all points
        cy.wait(1000);
        cy.get('canvas.mapboxgl-canvas').type('-');
        // check point count against fixture count
        cy.get('.map-point-count > i').should('contain', pointCount);
    });
    it('allows report to open on point selection', () => {
        cy.mount(GroundwaterLevel);
        cy.get('.q-virtual-scroll__content > .q-item:nth-child(1)').click();
        // details are displayed
        cy.get('.selected-point > pre:nth-child(1)').should('not.be.empty');
        cy.get('.q-btn > span > span').contains('View More').click();
        cy.get('.report-sidebar').should('exist').and('be.visible');
        cy.get('.q-list > .q-item:first()').should('have.class', 'active');
        cy.get('.d3-chart > g.g-els').should('exist').and('be.visible');
        cy.get('.q-list > .q-item:nth-child(2)').should('not.have.class', 'active').click();
        cy.get('.q-list > .q-item:nth-child(2)').should('have.class', 'active').click();
        cy.get('.q-table__title').should('contain', 'Monthly Mean Flow');
    });
});
