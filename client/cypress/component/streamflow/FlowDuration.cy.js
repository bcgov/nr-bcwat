import FlowDuration from '@/components/streamflow/FlowDuration.vue';
import flowDuration from '../../fixtures/flowDuration.json';

const data = flowDuration;

describe('<FlowDuration />', () => {
    beforeEach(() => {
        cy.intercept('/climate/stations', { fixture: 'flowDuration.json' });
    });
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
