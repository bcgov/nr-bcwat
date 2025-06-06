import ClimateReport from "@/components/climate/ClimateReport.vue";
import activePointClimate from '../../fixtures/activePointClimate.json';
import climateReport from '@/constants/climateReport.json';

const data = climateReport.getStation;

describe('<ClimateReport />', () => {
    it('mounts with report closed', () => {
        cy.mount(ClimateReport, {
            props: {
                reportOpen: false,
                reportContent: {},
                activePoint: {},
            },
        });
        cy.get('.report-container').should('not.have.class', 'open');
    });
    it('mounts with report open', () => {
        cy.mount(ClimateReport, {
            props: {
                reportOpen: true,
                reportContent: climateReport.getStation,
                activePoint: activePointClimate.properties,
            },
        });
        cy.get('.report-container').should('have.class', 'open');
    });
    it('renders all pages and charts', () => {
        cy.mount(ClimateReport, {
            props: {
                reportOpen: true,
                reportContent: climateReport.getStation,
                activePoint: activePointClimate.properties,
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
        cy.get('.text-h6').contains('Precipitation').parent().click();
        cy.get('.chart-area').should('exist').and('be.visible');
        cy.get('.text-h6').contains('Snow on Ground').parent().click();
        cy.get('.chart-area').should('exist').and('be.visible');
        cy.get('.text-h6').contains('Snow Water Equivalent').parent().click();
        cy.get('.chart-area').should('exist').and('be.visible');
        cy.get('.text-h6').contains('Manual Snow Survey').parent().click();
        cy.get('.chart-area').should('exist').and('be.visible');
    })
});
