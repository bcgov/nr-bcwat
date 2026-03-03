import WaterPortal from "@/components/water-portal/WaterPortal.vue";
import { portalHandler } from "@/utils/reactor.js";

describe('<ClimatePage />', () => {
    beforeEach(() => {
        cy.intercept('/climate/stations', { fixture: 'climateStations.json' });
        cy.intercept('/climate/**/report', { fixture: 'climateReport.json' });
    });

    it('mounts and renders components', () => {
        cy.mount(WaterPortal, {
            props: {
                defaultViewType: 'climate'
            }
        });
        portalHandler.updateViewType('climate');
        cy.get('.search-entry').should('exist');
        cy.get('.map-filters-container').should('exist');
    });
    it('opens report', () => {
        cy.mount(WaterPortal, {
            props: {
                defaultViewType: 'climate'
            }
        });
        portalHandler.updateViewType('climate');
        cy.get('.map-points-list > div')
            .children()
            .first()
            .click();
        cy.get('.q-btn > span > span').contains('View More').click();
        cy.get('.chart-area').should('exist').and('be.visible');

        // closes report
        cy.get('[data-cy="back-to-map"]').click();
        cy.get('.chart-area').should('not.exist');
    });
});
