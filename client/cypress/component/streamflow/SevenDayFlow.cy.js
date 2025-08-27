import SevenDayFlow from "@/components/streamflow/SevenDayFlow.vue";
import sevenDay from '../../fixtures/sevenDay.json';

const testSelectedPoint = {
    name: 'test point',
    yr: [2011, 2025]
}


describe('<SevenDayFlow />', () => {
    beforeEach(() => {
        cy.intercept('streamflow/**/report/seven-day-flow/**', { fixture: 'sevenDayHistorical.json' });
    })
    it('mounts and renders report chart', () => {
        cy.mount(SevenDayFlow, {
            props: {
                chartData: sevenDay,
                selectedPoint: testSelectedPoint
            }
        });
        // check that the chart's internal elements were loaded in
        cy.get('#chart-container > div > svg > g.g-els').should('exist');
    });
    it('handles adding and removing historical lines', () => {
        cy.mount(SevenDayFlow, {
            props: {
                chartData: sevenDay,
                selectedPoint: testSelectedPoint
            }
        });
        cy.get('.historical').should('not.exist')
        // open year historical dropdown
        cy.get('.yearly-input').click();
        cy.get('[data-cy="yearly-option-13"]').click();
        cy.get('.historical').should('exist')
        cy.get('[data-cy="yearly-option-10"]').click();
        cy.get('.historical').should('exist')
        cy.get('[data-cy="yearly-option-13"]').click();
        cy.get('.historical').should('exist')
        cy.get('[data-cy="yearly-option-10"]').click();
        cy.get('.historical').should('not.exist')
    });
});
