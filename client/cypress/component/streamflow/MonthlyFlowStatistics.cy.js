import MonthlyFlowStatistics from "../../../src/components/streamflow/MonthlyFlowStatistics.vue";
import monthlyFlowStatistics from '../../fixtures/monthlyFlowStatistics.json';

const chartData = monthlyFlowStatistics;
const axisElCount = 5;
const elsPerBoxPlot = 6;
const els = Object.keys(chartData).length * elsPerBoxPlot  + axisElCount;

describe('<MonthlyFlowStatistics />', () => {
    it('mounts and renders as expected', () => {
        cy.mount(MonthlyFlowStatistics, {
            props: {
                data: chartData,
                startEndYears: [1914, 1922],
                startEndMonths: ['Jan', 'Feb'],
            }
        });
        cy.get('.g-els').children().should('have.length', els);
    });
    it('brushes when user clicks and drags', () => {
        cy.mount(MonthlyFlowStatistics, {
            props: {
                data: chartData,
                startEndYears: [1914, 1922],
                startEndMonths: ['Jan', 'Feb'],
            }
        });

        cy.window().then(win => {
            cy.get('g[data-cy="mfs-chart-brush"] > rect.overlay')
                .trigger('mousedown', 10, 300, { which: 1, view: win })
                .trigger('mousemove', 300, 300, { which: 1, view: win })
                .trigger('mouseup', 300, 300, { which: 1, view: win })
        });

        // roughly checks the width of the rect that's drawn
        cy.get('rect.selection').should('exist').and('be.visible');
        cy.get('rect.selection').should('have.css', 'width').and('contain', '291');
    });
});
