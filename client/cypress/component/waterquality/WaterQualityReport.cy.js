import WaterQualityReport from '@/components/waterquality/WaterQualityReport.vue';
import sampleChemistry from '@/constants/surfaceWaterChemistry.json';

const chemistryTableLength = sampleChemistry.sparkline.length + 1;
const activeTestPoint = {
    name: '',
    nid: '',
    id: '',
    status: '',
    net: '',
    area: '',
    network: '',
    yr: [2012, 2025]
};

describe('WaterQualityReport', () => {
    it('mounts report and content', () => {
        cy.mount(WaterQualityReport, {
            props: {
                chemistry: sampleChemistry,
                reportType: 'Surface',
                reportOpen: true,
                activePoint: activeTestPoint,
            }
        });
        cy.get('.q-list > .q-item').should('have.class', 'active');
    });
    it('mini charts open ', () => {
        cy.mount(WaterQualityReport, {
            props: {
                chemistry: sampleChemistry,
                reportType: 'Surface',
                reportOpen: true,
                activePoint: activeTestPoint,
            }
        });
        // check that the correct number of rows of charts are displayed. 
        cy.get('.water-quality-table > tbody').children().should('have.length', chemistryTableLength);

        // verify popup chart
        cy.get('.mini-chart').first().click();
        cy.get('.surface-water-chart-container').should('exist').and('be.visible');
        cy.get('.q-icon').contains('close').click();
    });
});
