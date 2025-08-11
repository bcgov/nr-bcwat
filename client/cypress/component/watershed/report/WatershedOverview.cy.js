import WatershedOverview from "@/components/watershed/report/WatershedOverview.vue";
import watershedReport from '../../../fixtures/watershedReport.json';

const reportContent = watershedReport;

describe('<WatershedOverview />', () => {
    it('mounts and renders content', () => {
        cy.mount(WatershedOverview, {
            props: {
                reportContent
            }
        });
        cy.get('.q-timeline__content > .q-timeline__title').contains('Twain Creek');
        cy.get('.q-timeline__content > .q-timeline__title').contains('Babine River');
        cy.get('.q-timeline__content > .q-timeline__title').contains('Skeena River');
        cy.get('h2').contains('Twain Creek');
        cy.get('.overview-line').children().eq(1).should('contain', '54.606° N, -125.821° W');
        cy.get('.overview-line').children().eq(3).should('contain', '50.60 km2');
        cy.get('.overview-line').children().eq(5).should('contain', '1349.81 m (max), 1169.53 m (mean), 1021.41 m (min),');
        cy.get('.overview-line').children().eq(7).should('contain', '0.389 m3/s');
    });
});
