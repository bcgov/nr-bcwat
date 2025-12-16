import WaterPortal from "@/components/water-portal/WaterPortal.vue";
import { portalHandler } from '@/utils/reactor.js';
import groundWaterLevelStations from '../../fixtures/groundWaterLevelStations.json';

const pointCount = groundWaterLevelStations.features.length;

describe('<GroundwaterLevel />', () => {
    beforeEach(() => {
        cy.intercept('**/stations', { fixture: 'groundWaterLevelStations.json' });
        cy.intercept('**/report', { fixture: 'groundwaterLevel.json' });
    });

    it('mounts and renders the map', () => {
        cy.mount(WaterPortal, {
            props: {
                defaultViewType: 'wells'
            }
        });
        portalHandler.updateViewType('wells');
        cy.get('.mapboxgl-canvas').should('exist').and('be.visible');
        // zoom out of the map, showing all points
        cy.wait(1000);
        cy.get('canvas.mapboxgl-canvas').type('-');
        // check point count against fixture count
        cy.get('.map-point-count > div > i').should('contain', pointCount);
    });
    it('allows report to open on point selection', () => {
        cy.mount(WaterPortal, {
            props: {
                defaultViewType: 'wells'
            }
        });
        portalHandler.updateViewType('wells');
        cy.get('.map-points-list > div:nth-child(1) > .q-item').click();
        // details are displayed
        cy.get('.selected-point > pre:nth-child(1)').should('not.be.empty');
        cy.get('.q-btn > span > span').contains('View More').click();
        cy.get('.report-sidebar').should('exist').and('be.visible');
        cy.get('.q-list > .q-item:first()').should('have.class', 'active');
        cy.get('.d3-chart > g.g-els').should('exist').and('be.visible');
        cy.get('.q-list > .q-item:nth-child(2)').should('not.have.class', 'active').click();
        cy.get('.q-list > .q-item:nth-child(2)').should('have.class', 'active').click();
        cy.get('.q-table__title').should('contain', 'Monthly Mean Discharge');
    });
});
