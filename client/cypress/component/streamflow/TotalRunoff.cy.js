import TotalRunoff from "../../../src/components/streamflow/TotalRunoff.vue";
import flowDuration from '@/constants/flowDuration.json';

const chartData = flowDuration.totalRunoff;


describe('<MonthlyFlowStatistics />', () => {
    it('mounts and renders as expected', () => {
        cy.mount(TotalRunoff, {
            props: {
                data: chartData,
                startEndMonths: ['Jan', 'Feb'],
            }
        });
    });
    it('brushes when user clicks and drags', () => {
        cy.mount(TotalRunoff, {
            props: {
                data: chartData,
                startEndMonths: ['Jan', 'Feb'],
            }
        })

        cy.window().then(win => {
            cy.get('g[data-cy="tr-chart-brush"] > rect.overlay')
                .trigger('mousedown', 50, 10, { which: 1, view: win })
                .trigger('mousemove', 50, 40, { which: 1, view: win })
                .trigger('mouseup', 50, 40, { which: 1, view: win })
        })

        // roughly checks the height of the rect that's drawn
        cy.get('rect.selection').should('have.css', 'height').and('contain', '44');
    });
});
