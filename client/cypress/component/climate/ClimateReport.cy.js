import ClimateReport from "@/components/climate/ClimateReport.vue";
import activePointClimate from '../../fixtures/activePointClimate.json';
import climateReport from '@/constants/climateReport.json';

const data = climateReport.getStation;

describe('<ClimateReport />', () => {
    it('mounts with report closed', () => {
        cy.mount(ClimateReport, {
            props: {
                reportOpen: false,
                reportContent: climateReport.getStation,
                activePoint: activePointClimate.properties,
            },
        });
        cy.get('.d3-chart').should('not.exist')
    });
    it('mounts with report closed', () => {
        cy.mount(ClimateReport, {
            props: {
                reportOpen: true,
                reportContent: climateReport.getStation,
                activePoint: activePointClimate.properties,
            },
        });
        cy.get('#chart-container').should('exist').and('be.visible');
    });
});
