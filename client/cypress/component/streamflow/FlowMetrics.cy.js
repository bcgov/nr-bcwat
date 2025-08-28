import FlowMetrics from "@/components/streamflow/FlowMetrics.vue";
import flowMetrics from '../../fixtures/flowMetrics.json';

const tableData = flowMetrics;
const VALUE_IN_TABLE = 4.04;

describe('<FlowMetrics />', () => {
    it('mounts and renders chart as expected', () => {
        cy.mount(FlowMetrics, {
            props: {
                tableData
            }
        });
        // if the component doesn't get the data, it won't load. This check will ensure
        // that the table has received rows and columns. 
        cy.get('[data-cy="flow-metrics-table"]').should('exist').and('be.visible');
        cy.get('[data-cy="flow-metrics-table"] > div > table > tbody').children().should('have.length', 5);
        cy.get('[data-cy="flow-metrics-table"] > div > table > tbody > tr:nth-child(3) > td:nth-child(6)').should('contain', VALUE_IN_TABLE);
    });
});
