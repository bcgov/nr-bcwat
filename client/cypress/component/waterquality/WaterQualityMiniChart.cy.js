import WaterQualityMiniChart from '@/components/waterquality/WaterQualityMiniChart.vue';
import waterQualityMiniChart from '../../fixtures/waterQualityMiniChart.json';

const chartCurve = 'M0,0L29.624,27.429L109.688,80L180,64';

describe('<WaterQualityMiniChart />', () => {
    it('renders the mini-size chart', () => {
        cy.mount(WaterQualityMiniChart, {
            props: {
                chartData: waterQualityMiniChart,
                chartId: 'test-mini-chart',
            }
        });
        cy.get('#test-mini-chart').should('exist').and('be.visible');
        cy.get('#test-mini-chart > svg > g > path').should('have.attr', 'd').and('eq', chartCurve);
    });
});
