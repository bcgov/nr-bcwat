import SevenDayFlow from "@/components/streamflow/SevenDayFlow.vue";
import sevenDayFlow from '@/constants/sevenDayFlow.json';

const chartData = sevenDayFlow;
const testSelectedPoint = {
    name: 'test point',
    yr: [2011, 2025]
}

describe('<SevenDayFlow />', () => {
    it('mounts and renders report chart', () => {
        cy.mount(SevenDayFlow, {
            props: {
                chartData,
                selectedPoint: testSelectedPoint
            }
        });
    });
});
