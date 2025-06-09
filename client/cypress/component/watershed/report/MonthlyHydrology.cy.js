import MonthlyHydrology from "@/components/watershed/report/MonthlyHydrology.vue";
import watershedReport from "@/constants/watershedReport.json";

const reportContent = watershedReport;

describe('<MonthlyHydrology />', () => {
    it('mounts and renders content correctly', () => {
        cy.mount(MonthlyHydrology, {
            props: {
                reportContent
            }
        });
        cy.get('.monthly-hydrology-header > h1').should('contain', ' Monthly Water Supply and Demand - Hay River');
        cy.get('.monthly-hydrology-header > h1').should('contain', ' Monthly Water Supply and Demand - Hay River (Downstream) ');
        cy.get('#monthly-chart > svg > g > g:nth-child(3) > g:nth-child(3) > rect:nth-child(1)').should('have.attr', 'height').and('eq', '1.332660999855932');
        cy.get('#monthly-chart-downstream > svg > g > g:nth-child(3) > g:nth-child(3) > rect:nth-child(1)').should('have.attr', 'height').and('eq', '1.3731477254395372');
    });
});
