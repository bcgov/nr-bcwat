import Climate from "@/components/watershed/report/Climate.vue";
import watershedReport from '@/constants/watershedReport.json';

const reportContent = watershedReport; 

describe('<Climate />', () => {
    it('mounts and loads charts as expected', () => {
        cy.mount(Climate, {
            props: {
                reportContent
            }
        });
        cy.get('#climate-temperature-chart > svg > g > path').should('exist').and('be.visible');
        cy.get('#climate-precipitation-chart > svg > g > path').should('exist').and('be.visible');
        cy.get('#climate-snow-chart > svg > g > path').should('exist').and('be.visible');
    })
})
