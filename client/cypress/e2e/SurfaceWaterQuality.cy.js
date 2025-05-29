import surfaceWaterStations from '@/constants/surfaceWaterStations.json';
import surfaceWaterChemistry from '@/constants/surfaceWaterChemistry.json';

const count = surfaceWaterStations.features.length;
const chemistrylength = surfaceWaterChemistry.sparkline.length + 1;

describe('Surface Water Quality page', () => {
    it('loads and renders map', () => {
        cy.visit('/surface-water-quality');
        cy.get('canvas.mapboxgl-canvas').should('exist').and('be.visible');
        // map interaction - zoom out
        cy.wait(5000)
        cy.get('canvas.mapboxgl-canvas').type('-')
        cy.wait(1000)
        cy.get('canvas.mapboxgl-canvas').type('-')
        // when all points in BC are visible, check the listed count vs the data fixture
        cy.get('.map-point-count > i').contains(count);
    });
    
    it('open and renders chart content', () => {
        cy.visit('/surface-water-quality');
        cy.get('.q-item').first().click();
        cy.get('.q-btn > span > span').contains('View More').click();
        cy.get('.report-container').should('have.class', 'open');
        cy.get('.report-sidebar > .q-list').children().should('have.length', 1);
        cy.get('.report-sidebar > .q-list > .q-item').should('have.class', 'active');
        cy.get('.report-sidebar > .q-list > .q-item > div.text-h6').should('contain', 'Surface Water Quality');

        // check that the correct number of charts are displayed. 
        cy.get('.water-quality-table > tbody').children().should('have.length', chemistrylength);

        // closes report
        cy.get('.q-btn').contains('Back to Map').click();
        cy.get('.report-container').should('not.have.class', 'open');
        cy.get('canvas.mapboxgl-canvas').should('exist').and('be.visible');
    });
});
