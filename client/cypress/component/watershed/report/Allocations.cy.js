import Allocations from "@/components/watershed/report/Allocations.vue";
import watershedReport from '@/constants/watershedReport.json';
import { formatDate } from "@/utils/dateHelpers.js";

const reportData = watershedReport;
reportData.allocations.push({
    water_allocation_type: "SW",
    licence_term: "long",
    licence_term: "application",
    purpose_groups: "Agriculture",
    licensee: "Cypress",
    purpose: "Test Purpose",
    stream_name: "Test Stream",
    sourcetype: "Test Source",
    file_no: "1234",
    licence_no: "5678",
    file_no: "File Number 1234",
    pod: "POD",
    well_tag_number: "WellTagNumTest",
    start_date: new Date(),
    priority_date: new Date(),
    expiry_date: new Date(),
    lic_status_date: new Date(),
    qty_display: "1234",
    qty_flag: "Test",
    lic_type: "sw-lic",
    lic_status: "CURRENT",
    fs_id: "1234",
    documentation: [
        {
            fileName: "Test File.txt",
            linkUrl: "#"
        }
    ]
});

describe('<Allocations />', () => {
    it('loads and renders content', () => {
        cy.mount(Allocations, {
            props: {
                reportContent: reportData
            }
        });
        const allocationRow = reportData.allocations[0];
        // check the test data matches the content displayed
        cy.get('.q-table > tbody > tr > td:nth-child(1) > p:nth-child(1)').should('have.text', allocationRow.licensee);
        cy.get('.q-table > tbody > tr > td:nth-child(1) > p:nth-child(2)').should('contain', allocationRow.purpose).and('contain', allocationRow.stream_name);
        cy.get('.q-table > tbody > tr > td:nth-child(2) > p:nth-child(2)').should('contain', 'File # ' + allocationRow.file_no)
        cy.get('.q-table > tbody > tr > td:nth-child(3) > p:nth-child(1)').should('contain', allocationRow.pod);
        cy.get('.q-table > tbody > tr > td:nth-child(3) > p:nth-child(2)').should('contain', allocationRow.well_tag_number);
        cy.get('.q-table > tbody > tr > td:nth-child(4) > p:nth-child(1)').then(text => {
            assert(text[0].innerHTML.includes(formatDate(allocationRow.start_date, 'dd mmm yyyy', ' ')));
        })
        cy.get('.q-table > tbody > tr > td:nth-child(4) > p:nth-child(1)').should('contain', formatDate(allocationRow.start_date, 'dd mmm yyyy', ' '));
        cy.get('.q-table > tbody > tr > td:nth-child(4) > p:nth-child(2)').should('contain', formatDate(allocationRow.priority_date, 'dd mmm yyyy', ' '));
        cy.get('.q-table > tbody > tr > td:nth-child(4) > p:nth-child(3)').should('contain', formatDate(allocationRow.expiry_date, 'dd mmm yyyy', ' '));
        cy.get('.q-table > tbody > tr > td:nth-child(4) > p:nth-child(4)').should('contain', formatDate(allocationRow.lic_status_date, 'dd mmm yyyy', ' '));
        cy.get('.q-table > tbody > tr > td:nth-child(5)').should('contain', allocationRow.qty_display);
        cy.get('.q-table > tbody > tr > td:nth-child(6)').should('contain', allocationRow.qty_flag);
        cy.get('.q-table > tbody > tr > td:nth-child(7) > div').should('have.class', allocationRow.lic_type);
        cy.get('.q-table > tbody > tr > td:nth-child(7) > div').should('contain', allocationRow.lic_type);
        cy.get('.q-table > tbody > tr > td:nth-child(8) > .q-icon').should('have.class', 'mdi-check-circle').and('have.class', 'text-green-5')
    })
    it('sets and resets filters', () => {
        cy.mount(Allocations, {
            props: {
                reportContent: reportData
            }
        });
        const allocationRow = reportData.allocations[0];
        // check value exists before filtering
        cy.get('.q-table > tbody > tr > td:nth-child(5)').should('contain', allocationRow.qty_display);
        cy.get('.mdi-filter').click()
        cy.get('.q-checkbox__label').contains('Surface Water').click()
        cy.get('.q-table > tbody > tr > td:nth-child(5)').should('not.exist');
        cy.get('.q-checkbox__label').contains('Surface Water').click()
        cy.get('.q-table > tbody > tr > td:nth-child(5)').should('contain', allocationRow.qty_display);
        cy.get('.q-checkbox__label').contains('Application').click()
        cy.get('.q-table > tbody > tr > td:nth-child(5)').should('not.exist');
        cy.get('.q-checkbox__label').contains('Application').click();
        cy.get('.q-checkbox__label').contains('Agriculture').click();
        cy.get('.q-table > tbody > tr > td:nth-child(5)').should('not.exist');
        cy.get('.q-checkbox__label').contains('Agriculture').click();
        cy.get('.q-table > tbody > tr > td:nth-child(5)').should('contain', allocationRow.qty_display);
        cy.get('input[placeholder="Text Search"]').type('TESTING')
        cy.get('.q-table > tbody > tr > td:nth-child(5)').should('not.exist');
        cy.get('input[placeholder="Text Search"]').clear()
        cy.get('input[placeholder="Text Search"]').type('Cypress')
        cy.get('.q-table > tbody > tr > td:nth-child(5)').should('contain', allocationRow.qty_display);
        cy.get('span').contains('Reset Filters').click();
        cy.get('input[placeholder="Text Search"]').should('have.value', '');
    })
})
