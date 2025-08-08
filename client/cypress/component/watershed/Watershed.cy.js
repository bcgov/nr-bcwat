import Watershed from '@/components/watershed/Watershed.vue'

describe('<Watershed />', () => {
  beforeEach(() => {
      cy.intercept('/watershed/licences', { fixture: 'watershed.json' });
      cy.intercept('**/report', { fixture: 'watershedReport.json' });
      cy.intercept('**/watershed/?lat**', { fixture: 'watershedClickGeom.json' });
  });
  it.only('renders and mounts related components', () => {
    cy.mount(Watershed)
    cy.get('.search-bar-container').should('exist').and('be.visible');
  });
  it('opens station details', () => {
    cy.mount(Watershed)
    cy.get('.q-virtual-scroll__content').children().first().click();
    cy.get('.selected-point').should('exist').and('be.visible');
  });
  it('opens watershed report', () => {
    cy.mount(Watershed)
    cy.wait(5000)
    cy.get('[data-cy="search-type"]').click();
    cy.get('span').contains('Watershed Feature Id').click();
    cy.get('[data-cy="search-input"]').type('10426142');
    cy.get('.search-result').click();
    // point clicked - popup shows
    cy.get('.watershed-info-popup').should('exist');
    cy.get('[data-cy="view-report-button"]').click();
    // only will be visible and exist when the report is actually opened and its contents rendered.
    // cy.get('.report-content').should('exist').and('be.visible');
  });
});
