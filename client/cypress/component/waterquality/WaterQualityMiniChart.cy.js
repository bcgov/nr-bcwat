import WaterQualityMiniChart from '@/components/waterquality/WaterQualityMiniChart.vue';
import waterQualityMiniChart from '@/constants/WaterQualityMiniChart.json';

describe('<WaterQualityMiniChart />', () => {
    it('renders the mini-size chart', () => {
        cy.mount(WaterQualityMiniChart, {
            props: {
                chartData: waterQualityMiniChart,
                chartId: 'test-mini-chart',
            }
        })
    });
});
