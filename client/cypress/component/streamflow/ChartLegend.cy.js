import ChartLegend from '@/components/streamflow/ChartLegend.vue';

const legendList = [
    {
        label: "Item One",
        color: "rgb(0, 0, 0)",
    },
    {
        label: "Item Two",
        color: "rgb(255, 255, 255)",
    },
];

describe('<ChartLegend />', () => {
    it('mounts with the correct legend content', () => {
        cy.mount(ChartLegend, { props: {
            legendList
        }});
        legendList.forEach((el, idx) => {
            cy.get('.legend-color').eq(idx).should('have.css', 'background-color').and('eq', el.color);
            cy.get('[data-test="legend-label"]').eq(idx).should('have.text', el.label);
        })
    });
});
