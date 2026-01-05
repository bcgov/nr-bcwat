import WatershedSummary from '@/components/watershed/report/WatershedSummary.vue';
import reportContent from '../../../fixtures/watershedReport.json';

describe('WatershedSummary.vue', () => {
    it('mounts and renders content', () => {
        cy.mount(WatershedSummary, {
            props: {
                reportContent
            }
        });
        cy.get('.text-h5').contains('Twain Creek');
        cy.get('.q-timeline__content > .q-timeline__title').contains('Twain Creek');
        cy.get('.q-timeline__content > .q-timeline__title').contains('Babine River');
        cy.get('.q-timeline__content > .q-timeline__title').contains('Skeena River');
    });
});
