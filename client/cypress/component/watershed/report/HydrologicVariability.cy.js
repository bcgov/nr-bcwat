import HydrologicVariability from '@/components/watershed/report/HydrologicVariability.vue';
import watershedReport from '../../../fixtures/watershedReport.json';

const reportContent = watershedReport;

describe('<HydrologicVariability />', () => {
    it('mounts and renders', () => {
        cy.mount(HydrologicVariability, {
            props: {
                reportContent,
                clickedPoint: {
                    lat: 50,
                    lng: -122
                }
            }
        });
        cy.get('.hydrologic-map-legend > div').should('contain', 'Query Watershed');
        cy.get('#hydrologic-watershed-table > div > div > table > tbody > tr:nth-child(1) > td:nth-child(2) > div.text-capitalize.text-bold').should('contain', 'query watershed');
        cy.get('#hydrologic-watershed-table > div > div > table > tbody > tr:nth-child(2) > td:nth-child(2) > div:nth-child(3)').should('contain', 'Pinkut Creek Near Tintagel');
        // chart testing
        cy.get('#hydrologic-bar-chart').scrollIntoView();
        cy.get('#hydrologic-bar-chart > svg > g > g > .domain').should('exist').and('be.visible');
        cy.get('.hydrologic-tabular-data > tbody > tr:nth-child(3) > td:nth-child(3)').contains('0.15');
        cy.get('.hydrologic-tabular-data > tbody > tr:nth-child(3) > td:nth-child(3)').contains('0.22');
        cy.get('.hydrologic-tabular-data > tbody > tr:nth-child(3) > td:nth-child(3)').contains('0.17');
    });
});
