import GroundWaterLevelReport from '@/components/groundwater-level/GroundWaterLevelReport.vue';
import groundwaterLevel from '../../fixtures/groundwaterLevel.json';

const activeTestPoint = {
    name: '',
    nid: '',
    id: '',
    status: '',
    net: '',
    area: '',
    network: '',
    yr: [2012, 2025]
};

describe('<GroundWaterLevelReport />', () => {
    beforeEach(() => {
        cy.intercept('**/stations', { fixture: 'groundWaterLevelStations.json' });
    })

    it('mounts closed and does not render report contents', () => {
        cy.mount(GroundWaterLevelReport, {
            props: {
                reportOpen: false,
            }
        });
        cy.get('.report-sidebar').should('not.exist');
    });
    it('mounts and render report contents', () => {
        cy.mount(GroundWaterLevelReport, {
            props: {
                reportOpen: true,
                reportData: groundwaterLevel,
                activePoint: activeTestPoint
            }
        });
        cy.get('.report-sidebar').should('exist');
        cy.get('.q-list > .q-item:nth-child(1)').should('have.class', 'active');
        cy.get('.d3-chart > g.g-els').should('exist').and('be.visible');
        // check the "current" line is present on the chart. 
        cy.get('.line.median').should('exist').and('be.visible').and('have.attr', 'stroke').and('eq', '#999999')

        // switch to the monthly mean flow table:
        cy.get('.q-list > .q-item > div.text-h6').contains('Monthly Mean Levels').click()
        cy.get('.q-list > .q-item:nth-child(2)').should('have.class', 'active');
        cy.get('.q-table__title').should('contain', 'Monthly Mean Flow');
        // check the table for the one value present in the report fixture data:
        cy.get('.q-table > tbody > .q-tr:nth-child(4) > .text-right:nth-child(6)').should('contain', '2.5634');
    });
});
