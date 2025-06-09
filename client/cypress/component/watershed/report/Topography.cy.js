import Topography from "@/components/watershed/report/Topography.vue";
import watershedReport from "@/constants/watershedReport.json";

const reportContent = watershedReport;

describe('<Topography />', () => {
    it('mounts as expected', () => {
        cy.mount(Topography, {
            props: {
                reportContent
            }
        });
        cy.get('#topography-chart > svg > g > path').should('have.attr', 'fill').and('eq', '#d3d3d3');
    });
});
