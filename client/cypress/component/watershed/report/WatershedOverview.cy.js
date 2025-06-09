import WatershedOverview from "@/components/watershed/report/WatershedOverview.vue";
import watershedReport from "@/constants/watershedReport.json";

const reportContent = watershedReport;

describe('<WatershedOverview />', () => {
    it('mounts and renders content', () => {
        cy.mount(WatershedOverview, {
            props: {
                reportContent
            }
        });
        cy.get('.q-timeline__content > .q-timeline__title').contains('Hay River');
        cy.get('.q-timeline__content > .q-timeline__title').contains('MacKenzie River');
        cy.get('.q-timeline__content > .q-timeline__title').contains('Arctic Ocean');
        cy.get('h2').contains('Hay River');
        cy.get('.overview-line').children().eq(1).should('contain', '58.736° N, -120.008° W');
        cy.get('.overview-line').children().eq(3).should('contain', '4075.63 km');
        cy.get('.overview-line').children().eq(5).should('contain', '1043.08 m (max), 568.139 m (mean), 345.119 m (min),');
        cy.get('.overview-line').children().eq(7).should('contain', '13.664 m');
    });
});
