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
        cy.get('#note-8 > .note-text').should('contain', 'June 13, 2023');
        cy.get('#note-9 > .note-text').should('contain', 'June 13, 2023');
        cy.get('#note-10 > .note-text').should('contain', 'August 22, 2023');
    });
});
