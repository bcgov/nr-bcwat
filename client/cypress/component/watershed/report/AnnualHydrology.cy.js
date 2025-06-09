import AnnualHydrology from '@/components/watershed/report/AnnualHydrology.vue';
import watershedReport from '@/constants/watershedReport.json';
import { addCommas } from "@/utils/stringHelpers.js";

const reportContent = { 
    overview: watershedReport.overview, 
    annualHydrology: watershedReport.annualHydrology 
};

describe('<AnnualHydrology />' , () => {
    it('mounts as expected', () => {
        cy.mount(AnnualHydrology, {
            props: {
                reportContent,
                // clickedPoint is irrelevant for this component test, as it performs map movement
                clickedPoint: {
                    lat: 0,
                    lng: 0
                },
            },
        });

        // map renders marker
        cy.get('.mapboxgl-marker').should('exist')

        // check table for content where it is expected
        const annualHydrologyObj = reportContent.annualHydrology;
        // Area
        cy.get(`.annual-hydrology-table > tbody > tr:nth-child(2) > td:nth-child(1)`).should('contain', 'Area (km2)');
        cy.get(`.annual-hydrology-table > tbody > tr:nth-child(2) > td:nth-child(2)`).should('contain', (+annualHydrologyObj.area_km2.query).toFixed(0));
        cy.get(`.annual-hydrology-table > tbody > tr:nth-child(2) > td:nth-child(3)`).should('contain', (+annualHydrologyObj.area_km2.downstream).toFixed(0));
        // Mean Annual Discharge
        cy.get(`.annual-hydrology-table > tbody > tr:nth-child(3) > td:nth-child(1)`).should('contain', 'Mean Annual Discharge');
        cy.get(`.annual-hydrology-table > tbody > tr:nth-child(3) > td:nth-child(2)`).should('contain', (+annualHydrologyObj.mad_m3s.query).toFixed(3));
        cy.get(`.annual-hydrology-table > tbody > tr:nth-child(3) > td:nth-child(3)`).should('contain', (+annualHydrologyObj.mad_m3s.downstream).toFixed(3));
        // Allocations average m3/yr
        cy.get(`.annual-hydrology-table > tbody > tr:nth-child(4) > td:nth-child(1)`).should('contain', 'Allocations (average, m3/yr)');
        cy.get(`.annual-hydrology-table > tbody > tr:nth-child(4) > td:nth-child(2)`).should('contain', (+annualHydrologyObj.allocs_m3s.query).toFixed(3));
        cy.get(`.annual-hydrology-table > tbody > tr:nth-child(4) > td:nth-child(3)`).should('contain', (+annualHydrologyObj.allocs_m3s.downstream).toFixed(3));
        // Allocations average % of MAD: these are not fixed; these include string in the output values. 
        cy.get(`.annual-hydrology-table > tbody > tr:nth-child(5) > td:nth-child(1)`).should('contain', 'Allocations (average, % of MAD)');
        cy.get(`.annual-hydrology-table > tbody > tr:nth-child(5) > td:nth-child(2)`).should('contain', annualHydrologyObj.allocs_pct.query);
        cy.get(`.annual-hydrology-table > tbody > tr:nth-child(5) > td:nth-child(3)`).should('contain', annualHydrologyObj.allocs_pct.downstream);
        // Reserves & restrictions
        cy.get(`.annual-hydrology-table > tbody > tr:nth-child(6) > td:nth-child(1)`).should('contain', 'Reserves & Restrictions');
        cy.get(`.annual-hydrology-table > tbody > tr:nth-child(6) > td:nth-child(2)`).should('contain', annualHydrologyObj.rr.query);
        cy.get(`.annual-hydrology-table > tbody > tr:nth-child(6) > td:nth-child(3)`).should('contain', annualHydrologyObj.rr.downstream);
        // Volume Runoff
        cy.get(`.annual-hydrology-table > tbody > tr:nth-child(7) > td:nth-child(1)`).should('contain', 'Volume Runoff');
        cy.get(`.annual-hydrology-table > tbody > tr:nth-child(7) > td:nth-child(2)`).should('contain', addCommas((+annualHydrologyObj.runoff_m3yr.query).toFixed(0)));
        cy.get(`.annual-hydrology-table > tbody > tr:nth-child(7) > td:nth-child(3)`).should('contain', addCommas((+annualHydrologyObj.runoff_m3yr.downstream).toFixed(0)));
        // // Volume Allocations
        cy.get(`.annual-hydrology-table > tbody > tr:nth-child(8) > td:nth-child(1)`).should('contain', 'Volume Allocations');
        cy.get(`.annual-hydrology-table > tbody > tr:nth-child(8) > td:nth-child(2)`).should('contain', addCommas((+annualHydrologyObj.allocs_m3yr.query).toFixed(0)));
        cy.get(`.annual-hydrology-table > tbody > tr:nth-child(8) > td:nth-child(3)`).should('contain', addCommas((+annualHydrologyObj.allocs_m3yr.downstream).toFixed(0)));
        // // Seasonal Flow Sensitivity
        cy.get(`.annual-hydrology-table > tbody > tr:nth-child(9) > td:nth-child(1)`).should('contain', 'Seasonal Flow Sensitivity');
        cy.get(`.annual-hydrology-table > tbody > tr:nth-child(9) > td:nth-child(2)`).should('contain', annualHydrologyObj.seasonal_sens.query);
        cy.get(`.annual-hydrology-table > tbody > tr:nth-child(9) > td:nth-child(3)`).should('contain', annualHydrologyObj.seasonal_sens.downstream);
    });
});
