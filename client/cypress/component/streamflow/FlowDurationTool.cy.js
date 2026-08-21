// while child components of the flow duration tool are being testing elsewhere,
// this spec provides some integration testing and facilitates interaction between
// the various charts.

import FlowDurationTool from '@/components/streamflow/FlowDurationTool.vue';
import flowDuration from '../../fixtures/flowDuration.json';

describe('<FlowDurationTool />', () => {
    it('mounts and renders charts', () => {
        cy.mount(FlowDurationTool, {
            props: {
                chartData: flowDuration
            }
        });
        cy.get('.d3-chart-mf').should('exist');
        cy.get('.d3-chart-fd').should('exist');
        cy.get('.streamflow-chart-runoff').should('exist');

        // check the brushed area does not yet exist
        cy.get('.mfs-chart-brush > .selection').should('exist').and('have.attr', 'style').and('eq', 'display: none;');

        cy.get('[data-cy="month-selector"]').click();
        cy.get('.q-virtual-scroll__content > .q-item:nth-child(4)').click();

        // check the brushed appeared after selecting a month from the total runoff dropdown
        cy.get('.mfs-chart-brush > .selection').should('exist').and('have.attr', 'style').and('not.eq', 'display: none;');

        // check year selection sets range
        cy.get('[data-cy="year-from-selector"]').click();
        cy.get('[data-cy="year-from-option-0"]').click();
        cy.get('[data-cy="year-to-selector"]').click();
        cy.get('[data-cy="year-to-option-2"]').click();
        // after setting range, brush should exist
        cy.get('g[data-cy="tr-chart-brush"]').should('exist').and('be.visible');
    });
});
