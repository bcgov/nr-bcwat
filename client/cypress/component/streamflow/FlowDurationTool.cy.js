// while child components of the flow duration tool are being testing elsewhere, 
// this spec provides some integration testing and facilitates interaction between
// the various charts. 

import FlowDurationTool from '@/components/streamflow/FlowDurationTool.vue';
import flowDuration from '@/constants/flowDuration.json';

describe('<FlowDurationTool />', () => {
    it('mounts and renders charts', () => {
        cy.mount(FlowDurationTool, {
            props: {
                chartData: flowDuration
            }
        });
        cy.get('.d3-chart-mf').should('exist');
        cy.get('.d3-chart-fd').should('exist');
        cy.get('.d3-chart-tr').should('exist');

        // check the brushed area does not yet exist
        cy.get('.d3-chart-mf > g > .selection').should('exist').and('have.attr', 'style').and('eq', 'display: none;');

        cy.get('[data-cy="month-selector"]').click();
        cy.get('.q-virtual-scroll__content > .q-item:nth-child(4)').click();

        // check the brushed appeared after selecting a month from the total runoff dropdown
        cy.get('.d3-chart-mf > g > .selection').should('exist').and('have.attr', 'style').and('not.eq', 'display: none;');
    });
});
