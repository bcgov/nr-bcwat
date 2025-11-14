import WatershedReport from '@/components/watershed/WatershedReport.vue';
import watershedReport from '../../fixtures/watershedReport.json';

const reportData  = watershedReport;

describe('<WatershedReport />', () => {
    it('renders report contents', () => {
        cy.mount(WatershedReport, {
            props: {
                reportOpen: true,
                reportContent: reportData,
                clickedPoint: { lng: -122, lat: 50 },
                wfi: '123'
            }
        });
        cy.get('#header').should('contain', reportData.overview.watershedName);
    });
});
