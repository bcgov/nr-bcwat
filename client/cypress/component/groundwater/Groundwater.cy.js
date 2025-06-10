import GroundWater from "@/components/groundwater/GroundWater.vue";

describe('<GroundWater />', () => {
    it('mounts and loads main page contents', () => {
        cy.mount(GroundWater);
        cy.get('.mapboxgl-canvas').should('exist').and('be.visible')
    });
});
