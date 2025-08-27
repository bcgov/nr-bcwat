import Notes from "@/components/watershed/report/Notes.vue";
import watershedReport from '../../../fixtures/watershedReport.json';

const reportContent = watershedReport;

describe('<Notes />', () => {
    it('renders the correct notes', () => {
        cy.mount(Notes, {
            props: {
                reportContent
            }
        });
        cy.get('#note-8 > .note-text').should('contain', 'Water Rights Licences imported');
        cy.get('#note-9 > .note-text').should('contain', 'Water Rights Applications imported');
        cy.get('#note-10 > .note-text').should('contain', 'FLNRORD Water Approval Points imported');
    });
});
