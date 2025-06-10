import Landcover from '@/components/watershed/report/Landcover.vue';
import watershedReport from '@/constants/watershedReport.json';

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
            .and('eq', 'M71.1,170.791A185,185,0,0,1,-182.377,-31.044L0,0Z');
        cy.get('.q-table > tbody > .q-tr:nth-child(5) > td:nth-child(2)').should('contain', 'Developed');
    });
});
