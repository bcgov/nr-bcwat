import Landcover from '@/components/watershed/report/Landcover.vue';
import watershedReport from '../../../fixtures/watershedReport.json';

const reportContent = watershedReport;

describe('<Landcover />', () => {
    it('mounts and renders pie chart', () => {
        cy.mount(Landcover, {
            props: {
                reportContent
            }
        });
        cy.get('h1').should('contain', 'Landcover');
        cy.get('#landcover-pie-chart > svg > g > path:nth-child(2)')
            .should('have.attr', 'd')
            .and('eq', 'M0,-185A185,185,0,1,1,-123.473,-137.766L0,0Z');
        cy.get('.q-table > tbody > .q-tr:nth-child(5) > td:nth-child(2)').should('contain', 'Developed');
    });
});
