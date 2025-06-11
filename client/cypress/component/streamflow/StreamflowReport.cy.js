import StreamflowReport from "@/components/streamflow/StreamflowReport.vue";
import sevenDay from "@/constants/sevenDay.json";
import sevenDayHistorical from "@/constants/sevenDayHistorical.json";
import flowDuration from "@/constants/flowDuration.json";
import flowMetrics from "@/constants/flowMetrics.json";
import monthlyMeanFlow from "@/constants/monthlyMeanFlow.json";

const activeTestPoint = {
    name: '',
    nid: '',
    id: '',
    status: '',
    net: '',
    area: '',
    network: '',
    yr: [2012, 2025]
}
const reportData = {
    sevenDayFlow: {
        current: sevenDay,
        historical: sevenDayHistorical
    },
    flowDuration,
    flowMetrics,
    monthlyMeanFlow,
    stage: {
        current: sevenDay,
        historical: sevenDayHistorical
    }
};

describe('<StreamflowReport />', () => {
    it('mounts no content when specified prop is false', () => {
        cy.mount(StreamflowReport, {
            props: {
                // in this case, there is nothing to show, the component is not rendered. 
                // the other props are not required and have default values
                reportOpen: false,
            }
        })
        cy.get('.report-sidebar').should('not.exist')
    })
    it('mounts and renders report contents', () => {
        cy.mount(StreamflowReport, {
            props: {
                reportOpen: true,
                activePoint: activeTestPoint,
                reportData
            }
        })
        cy.get('.report-sidebar').should('exist').and('be.visible');
    })
    it('loads prop data into other components correctly', () => {
        cy.mount(StreamflowReport, {
            props: {
                reportOpen: true,
                activePoint: activeTestPoint,
                reportData
            }
        });
        // check the default selected tab is correct
        cy.get('.q-list > .q-item:nth-child(1)').should('have.class', 'active');
        cy.get('.d3-chart > g.g-els').should('exist').and('be.visible');
        // flow duration tool
        cy.get('.report-sidebar > .q-list').children().eq(1).click();
        cy.get('#flow-duration-chart-container > .svg-wrap-mf > .d3-chart-mf > .g-els').should('exist');
        cy.get('#total-runoff-chart-container > .svg-wrap-fd > .d3-chart-fd > .g-els').should('exist').and('be.visible');
        cy.get('.d3-chart-tr > .g-els').should('exist')
        cy.get('.d3-chart-tr > .g-els').scrollIntoView(); // element exists, but out of viewport range (1000 x 1000)
        cy.get('.d3-chart-tr > .g-els').should('exist').and('be.visible');
        // flow metrics table
        cy.get('.report-sidebar > .q-list').children().eq(2).click();
        cy.get('.q-table > tbody').children().should('have.length', 5);
        // monthly mean flow table
        cy.get('.report-sidebar > .q-list').children().eq(3).click();
        cy.get('.q-table > tbody').children().should('have.length', 5);
        // stage chart
        cy.get('.report-sidebar > .q-list').children().eq(4).click();
        cy.get('#seven-day-flow-chart > #chart-container > .svg-wrap > .d3-chart > .g-els').should('exist').and('be.visible');
    });
});
