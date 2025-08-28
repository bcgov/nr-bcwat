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
        cy.intercept('**/stations/**/report/hydrograph/**', { fixture: 'groundwaterLevelYearly.json' });
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

        // check yearly data lines get added
        cy.get('.yearly-input').click();
        cy.get('[data-cy="yearly-option-0"]').click();
        cy.get('[data-cy="yearly-option-1"]').click();
        cy.get('.year2025.historical.line').should('exist');
        cy.get('.year2024.historical.line').should('exist');

        // switch to the monthly mean flow table:
        cy.get('.q-list > .q-item > div.text-h6').contains('Monthly Mean Levels').click()
        cy.get('.q-list > .q-item:nth-child(2)').should('have.class', 'active');
        cy.get('.q-table__title').should('contain', 'Monthly Mean Discharge');
        // check the table for the one value present in the report fixture data:
        cy.get('.q-table > tbody > tr:nth-child(4) > td:nth-child(7)').should('contain', '60.0147');
    });
});
