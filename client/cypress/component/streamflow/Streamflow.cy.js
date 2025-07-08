import Streamflow from '@/components/streamflow/Streamflow.vue';
import streamflow from '../../fixtures/streamflow.json';

const pointCount = streamflow.features.length;

describe('<Streamflow />', () => {
    it('loads and renders map with contents', () => {
        cy.mount(Streamflow);
        // check that the map element has rendered
        cy.get('.mapboxgl-canvas').should('exist').and('be.visible');
        // zoom out of the map, showing all points
        cy.wait(1000)
        cy.get('canvas.mapboxgl-canvas').type('-')
        cy.wait(1000)
        cy.get('canvas.mapboxgl-canvas').type('-')
        // check point count against fixture count
        cy.get('.map-point-count > i').should('contain', pointCount);
        // integration/e2e tests have been written that better test for the various
        // sub-components of this page, and its functionality. 
    });
});
