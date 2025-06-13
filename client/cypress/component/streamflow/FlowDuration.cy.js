import FlowDuration from '@/components/streamflow/FlowDuration.vue';
import flowDuration from '@/constants/flowDuration.json';

const data = flowDuration.flowDuration;

describe('<FlowDuration />', () => {
    it('mounts and renders', () => {
        cy.mount(FlowDuration, {
            props: {
                data,
                startEndYears: [1994, 2025],
                startEndMonths: ['Dec', 'Jan']
            }
        })
    });
});
