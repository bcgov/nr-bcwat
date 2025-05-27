import Watershed from '@/components/watershed/Watershed.vue'

describe('<Watershed />', () => {
  it('renders and mounts related components', () => {
    cy.mount(Watershed)
    cy.get('.search-bar-container').should('exist').and('be.visible');
  });
  it('opens station details', () => {
    cy.mount(Watershed)
    cy.get('.q-virtual-scroll__content').children().first().click();
    cy.get('.q-btn > span > span').contains('View More').click();
  });
  it('opens watershed report', () => {
    cy.mount(Watershed)
    cy.get('.mapboxgl-canvas').click();
    cy.get('.q-btn > span > span').contains('REPORT').click();
    // only will be visible and exist when the report is actually opened and its contents rendered.zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
    cy.get('.report-content').should('exist').and('be.visible');
  });
});
