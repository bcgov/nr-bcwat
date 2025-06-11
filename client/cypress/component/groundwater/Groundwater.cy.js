import GroundWater from "@/components/groundwater/GroundWater.vue";
import groundWaterStations from '@/constants/groundWaterStations.json';

const pointCount = groundWaterStations.features.length;

describe('<GroundWater />', () => {
    it('mounts and loads main page contents', () => {
        cy.mount(GroundWater);
        cy.get('.mapboxgl-canvas').should('exist').and('be.visible')
        // zoom out of the map, showing all points
        cy.wait(1000);
        cy.get('canvas.mapboxgl-canvas').type('-');
        // check point count against fixture count
        cy.get('.map-point-count > i').should('contain', pointCount);
    });
    it('mounts and loads report contents', () => {
        cy.mount(GroundWater);
        cy.get('.q-virtual-scroll__content > .q-item:nth-child(1)').click();
        // details are displayed
        cy.get('.selected-point > pre:nth-child(1)').should('not.be.empty');
        // open report
        cy.get('.q-btn > span > span').contains('View More').click();

        // check rows for quality charts
        cy.get('.water-quality-table > tbody').children().should('have.length', 64)
    });
});
