import WaterPortal from "@/components/water-portal/WaterPortal.vue";
import { portalHandler } from '@/utils/reactor.js';
import surfaceWaterStations from '../../fixtures/surfaceWaterStations.json';

const pointCount = surfaceWaterStations.features.length;

describe('<SurfaceWater />', () => {
    beforeEach(() => {
        cy.intercept('**/stations', { fixture: 'surfaceWaterStations.json' });
        cy.intercept('**/report', { fixture: 'surfaceWaterChemistry.json' });
        cy.intercept('**/station-statistics', {fixture: 'stationStatistics.json'});
    })
    it('mounts and loads main page contents', () => {
        cy.mount(WaterPortal, {
            props: {
                defaultViewType: 'surface'
            }
        });
        portalHandler.updateViewType('surface');
        cy.get('.mapboxgl-canvas').should('exist').and('be.visible')
        // zoom out of the map, showing all points
        cy.wait(1000);
        cy.get('canvas.mapboxgl-canvas').type('-');
        // check point count against fixture count
        cy.get('.map-point-count > div > i').should('contain', pointCount);
    });
    it('mounts and loads report contents', () => {
        cy.mount(WaterPortal, {
            props: {
                defaultViewType: 'surface'
            }
        });
        portalHandler.updateViewType('surface');
        cy.get('.map-points-list > div:nth-child(1) > .q-item').click();
        // details are displayed
        cy.get('.selected-point > pre:nth-child(1)').should('not.be.empty');
        // open report
        cy.get('.q-btn > span > span').contains('View More').click();

        // check rows for quality charts
        cy.get('.water-quality-table > tbody').children().should('have.length', 3)
    });
});
