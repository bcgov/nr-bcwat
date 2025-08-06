import GroundWaterQuality from "@/components/groundwater/GroundWaterQuality.vue";
import groundWaterStations from '../../fixtures/groundWaterStations.json';

const pointCount = groundWaterStations.features.length;

describe('<GroundWaterQuality />', () => {
    beforeEach(() => {
        cy.intercept('**/stations', { fixture: 'groundWaterStations.json' });
        cy.intercept('**/report', { fixture: 'groundWaterChemistry.json' });
    });

    it('mounts and loads main page contents', () => {
        cy.mount(GroundWaterQuality);
        cy.get('.mapboxgl-canvas').should('exist').and('be.visible')
        // zoom out of the map, showing all points
        cy.wait(1000);
        cy.get('canvas.mapboxgl-canvas').type('-');
        // check point count against fixture count
        cy.get('.map-point-count > div > i').should('contain', pointCount);
    });
    it('mounts and loads report contents', () => {
        cy.mount(GroundWaterQuality);
        cy.get('.q-virtual-scroll__content > .q-item:first').click();
        // details are displayed
        cy.get('.selected-point').should('not.be.empty');
        // // open report
        cy.get('.q-btn > span > span').contains('View More').click();

        // // check rows for quality charts
        cy.get('.water-quality-table > tbody').children().should('have.length', 64);
    });
});
