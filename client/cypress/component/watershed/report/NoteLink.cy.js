import NoteLink from "@/components/watershed/report/NoteLink.vue";

describe('<NoteLink />', () => {
    it('mounts and renders the correct note contents', () => {
        cy.mount(NoteLink, {
            props: {
                noteNumber: 6
            }
        });
        cy.get('.note-link > sup').should('contain', '6');
    });
    it('mounts and renders the correct note contents', () => {
        cy.mount(NoteLink, {
            props: {
                noteNumber: 99
            }
        });
        // although there is no 99 note, the component should still list the correct number. 
        cy.get('.note-link > sup').should('contain', '99');
    });
});
