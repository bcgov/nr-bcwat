import WaterPortal from "@/components/water-portal/WaterPortal.vue";
import groundWaterStations from '../../fixtures/groundWaterStations.json';
import { portalHandler } from '@/utils/reactor.js';

const pointCount = groundWaterStations.features.length;

describe('<GroundWaterQuality />', () => {
    beforeEach(() => {
        cy.intercept('**/stations', { fixture: 'groundWaterStations.json' });
        cy.intercept('**/report', { fixture: 'groundWaterChemistry.json' });
        cy.intercept('**/station-statistics', { fixture: 'stationStatistics.json' });
    });

    it('mounts and loads main page contents', () => {
        cy.mount(WaterPortal, {
            props: {
                defaultViewType: 'ground'
            }
        });
        portalHandler.updateViewType('ground');
        cy.get('.mapboxgl-canvas').should('exist').and('be.visible')
        // check point count against fixture count
        cy.get('.mapboxgl-canvas').type('-');
        cy.get('.map-point-count > div > i').should('contain', pointCount);
        cy.get('.mapboxgl-canvas').type('+');
        cy.get('.mapboxgl-canvas').type('{downArrow}');
        cy.wait(100);
        cy.get('.mapboxgl-canvas').type('+');
        cy.wait(100);
        cy.get('.mapboxgl-canvas').type('+');
        cy.wait(100);
        cy.get('.mapboxgl-canvas').type('+');
        cy.get('.map-point-count > div > i').contains(1);
    });
    it('mounts and loads report contents a expected', () => {
        cy.mount(WaterPortal, {
            props: {
                defaultViewType: 'ground'
            }
        });
        portalHandler.updateViewType('ground');
        cy.wait(1000);
        cy.get('.map-points-list > div')
            .children()
            .first()
            .click();
        cy.wait(1000);
        cy.get('.q-item').first().click();
        // details are displayed
        cy.get('.selected-point').should('not.be.empty');
        // open report
        cy.get('.q-btn > span > span').contains('View More').click();

        // check rows for quality charts
        cy.get('.water-quality-table > tbody').children().should('have.length', 64);
    });
});
