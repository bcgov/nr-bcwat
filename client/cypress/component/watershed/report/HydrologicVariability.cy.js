import HydrologicVariability from '@/components/watershed/report/HydrologicVariability.vue';
import watershedReport from '@/constants/watershedReport.json';

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
        cy.get('.hydrologic-watershed-table > tbody > .query-row > .border-bottom > table > tbody > tr:first() > td:nth-child(2) > b').should('contain', 'Query Watershed');
        cy.get('table.hydrologic-watershed-table > tbody > tr:nth-child(4) > td:nth-child(1) > table > tbody > tr:nth-child(3) > td:nth-child(2)').should('contain', 'Clear River Near Bear Canyon');
        cy.get('table.hydrologic-watershed-table > tbody > tr:nth-child(11) > td:nth-child(1) > table > tbody > tr:nth-child(3) > td:nth-child(2)').should('contain', 'Adsett Creek At Kilometre 386.0 Alaska Highway');
        // chart testing
        cy.get('#hydrologic-bar-chart').scrollIntoView();
        cy.get('#hydrologic-bar-chart > svg > g > g > .domain').should('exist').and('be.visible');
        cy.get('.hydrologic-tabular-data > tbody > tr:nth-child(3) > td:nth-child(3)').contains('1.60');
        cy.get('.hydrologic-tabular-data > tbody > tr:nth-child(3) > td:nth-child(3)').contains('2.94');
        cy.get('.hydrologic-tabular-data > tbody > tr:nth-child(3) > td:nth-child(3)').contains('1.87');
    });
});
