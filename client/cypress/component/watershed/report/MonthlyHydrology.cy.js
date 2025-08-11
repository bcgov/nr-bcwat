import MonthlyHydrology from "@/components/watershed/report/MonthlyHydrology.vue";
import watershedReport from '../../../fixtures/watershedReport.json';

const reportContent = watershedReport;

describe('<MonthlyHydrology />', () => {
    it('mounts and renders content correctly', () => {
        cy.mount(MonthlyHydrology, {
            props: {
                reportContent
            }
        });
        cy.get('.monthly-hydrology-header > h1').should('contain', ' Monthly Water Supply and Demand - Twain Creek');
        cy.get('.monthly-hydrology-header > h1').should('contain', ' Monthly Water Supply and Demand - Twain Creek (Downstream) ');
    });
});
