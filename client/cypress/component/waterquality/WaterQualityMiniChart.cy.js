import WaterQualityMiniChart from '@/components/waterquality/WaterQualityMiniChart.vue';
import waterQualityMiniChart from '@/constants/waterQualityMiniChart.json';

const chartCurve = 'M0,0L4.937,4.571C9.875,9.143,19.749,18.286,38.03,31.619C56.312,44.952,83,62.476,108.062,68.571C133.125,74.667,156.563,69.333,168.281,66.667L180,64';

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
