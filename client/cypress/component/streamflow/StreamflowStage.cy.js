import StreamflowStage from "@/components/streamflow/StreamflowStage.vue";
import sevenDayFlow from '../../fixtures/sevenDayFlow.json';

const chartData = {
    current: sevenDayFlow,
    historical: [],
};
const testSelectedPoint = {
    name: 'test point',
    yr: [2011, 2025]
}

describe('<SevenDayFlow />', () => {
    it('mounts and renders report chart', () => {
        cy.mount(StreamflowStage, {
            props: {
                chartData,
                selectedPoint: testSelectedPoint
            }
        });
        // check that the chart's internal elements were loaded in
        cy.get('#chart-container > div > svg > g.g-els').should('exist');
    });
    it('handles adding and removing historical lines', () => {
        cy.mount(StreamflowStage, {
            props: {
                chartData,
                selectedPoint: testSelectedPoint
            }
        });
        cy.get('.historical').should('not.exist')
        // open year historical dropdown
        cy.get('.yearly-input').click();
        cy.get('.q-virtual-scroll__content > .q-item:nth-child(2) > .q-item__section > .q-item__label > span').contains('2012').click();
        cy.get('.historical').should('exist')
        cy.get('.q-virtual-scroll__content > .q-item:nth-child(5) > .q-item__section > .q-item__label > span').contains('2015').click();
        cy.get('.historical').should('exist')
        cy.get('.q-virtual-scroll__content > .q-item:nth-child(2) > .q-item__section > .q-item__label > span').contains('2012').click();
        cy.get('.historical').should('exist')
        cy.get('.q-virtual-scroll__content > .q-item:nth-child(5) > .q-item__section > .q-item__label > span').contains('2015').click();
        cy.get('.historical').should('not.exist')
    });
});
