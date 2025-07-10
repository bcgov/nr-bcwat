import ClimateReport from "@/components/climate/ClimateReport.vue";
import activePointClimate from '../../fixtures/activePointClimate.json';
import climateReport from '../../fixtures/climateReport.json';

const data = climateReport;
const pointData = activePointClimate;

describe('<ClimateReport />', () => {
    it('mounts with report closed', () => {
        cy.mount(ClimateReport, {
            props: {
                reportOpen: false,
                reportContent: data,
                activePoint: pointData.properties,
            },
        });
        cy.get('.report-container').should('not.have.class', 'open');
    });
    it('mounts with report open', () => {
        cy.mount(ClimateReport, {
            props: {
                reportOpen: true,
                reportContent: data,
                activePoint: pointData.properties,
            },
        });
        cy.get('.report-container').should('have.class', 'open');
        cy.wait(1000)
    });
    it('renders all pages and charts', () => {
        cy.mount(ClimateReport, {
            props: {
                reportOpen: true,
                reportContent: data,
                activePoint: pointData.properties,
            },
        });

        cy.get('.report-container').should('have.class', 'open');
        // // temperature is active by default
        cy.get('.q-list').children().eq(0).should('have.class', 'active');
        cy.get('.q-list').children().eq(1).should('not.have.class', 'active');
        cy.get('.q-list').children().eq(2).should('not.have.class', 'active');
        cy.get('.q-list').children().eq(3).should('not.have.class', 'active');
        cy.get('.q-list').children().eq(4).should('not.have.class', 'active');

        // click through nav and check charts
        // waits added to ensure rendering elements
        cy.get('.text-h6').contains('Precipitation').click();
        cy.get('[data-cy="report-chart-area"]').should('exist').and('be.visible');
        cy.get('.text-h6').contains('Snow on Ground').click();
        cy.get('[data-cy="report-chart-area"]').should('exist').and('be.visible');
        cy.get('.text-h6').contains('Snow Water Equivalent').click();
        cy.get('[data-cy="report-chart-area"]').should('exist').and('be.visible');
        cy.get('.text-h6').contains('Manual Snow Survey').click();
        cy.get('div.no-data').should('exist').and('be.visible');
    })
});
