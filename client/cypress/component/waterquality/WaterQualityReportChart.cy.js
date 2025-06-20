import WaterQualityReportChart from '@/components/waterquality/WaterQualityReportChart.vue';
import sampleChemistry from '@/constants/surfaceWaterChemistry.json';

const chartData = sampleChemistry.sparkline[0];

describe('<WaterQualityReportChart />', () => {
    it('mounts and renders chart popup content', () => {
        cy.mount(WaterQualityReportChart, {
            props: {
                chartData,
                chartId: 'test',
            }
        });
        cy.get('.surface-water-chart-container > #test').should('exist').and('be.visible');
    });

    it('chart interaction', () => {
        cy.mount(WaterQualityReportChart, {
            props: {
                chartData,
                chartId: 'test',
            }
        });
        cy.get('.water-quality-point').then(res => {
            expect(res).to.have.length(5);
        });
        cy.get('#test > svg > g > circle:nth-child(11)').trigger('mousemove');
        cy.get('#test > svg > g > circle:nth-child(11)').should('have.attr', 'fill').and('eq', 'white');
        cy.get('.surface-water-tooltip').should('exist').and('be.visible');
    });
});
