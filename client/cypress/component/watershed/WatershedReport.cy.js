import WatershedReport from '@/components/watershed/WatershedReport.vue';
import watershedReport from '@/constants/watershedReport.json';

const reportContent  = watershedReport;

describe('<WatershedReport />', () => {
    it('renders report contents', () => {
        cy.mount(WatershedReport, {
            props: {
                reportOpen: true,
                reportContent,
                clickedPoint: { lng: -122, lat: 50 }
            }
        });
        cy.get('#overview > h1').should('contain', 'Overview');
    });
});
