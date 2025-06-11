import WaterQualityMiniChart from '@/components/waterquality/WaterQualityMiniChart.vue';
import waterQualityMiniChart from '@/constants/waterQualityMiniChart.json';

describe('<WaterQualityMiniChart />', () => {
    it('renders the mini-size chart', () => {
        cy.mount(WaterQualityMiniChart, {
            props: {
                chartData: waterQualityMiniChart,
                chartId: 'test-mini-chart',
            }
        });
        cy.get('#test-mini-chart').should('exist').and('be.visible');
    });
});
