import Allocations from "@/components/watershed/report/Allocations.vue";
import watershedReport from '../../../fixtures/watershedReport.json';
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
    display_ann_qty: 1234,
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

reportData.overview.lic_count = 1;

describe('<Allocations />', () => {
    it('loads and renders content', () => {
        cy.mount(Allocations, {
            props: {
                reportContent: reportData
            }
        });
        const allocationRow = reportData.allocations[0];
        // check the test data matches the content displayed

        cy.get('[data-cy="license"] > p:nth-child(1)').should('have.text', allocationRow.licensee);
        cy.get('[data-cy="license"] > p:nth-child(2)').should('contain', allocationRow.purpose).and('contain', allocationRow.stream_name);
        cy.get('[data-cy="number"] > p:nth-child(2)').should('contain', 'File # ' + allocationRow.file_no);
        cy.get('[data-cy="pod"] > p:nth-child(1)').should('contain', allocationRow.pod);
        cy.get('[data-cy="pod"] > p:nth-child(2)').should('contain', allocationRow.well_tag_number);
        cy.get('[data-cy="date"] > p:nth-child(1)').then(text => {
            assert(text[0].innerHTML.includes(formatDate(allocationRow.start_date, 'ddd mmm yyyy', ' ')));
        });
        cy.get('[data-cy="date"] > p:nth-child(1)').should('contain', formatDate(allocationRow.start_date, 'ddd mmm yyyy', ' '));
        cy.get('[data-cy="date"] > p:nth-child(2)').should('contain', formatDate(allocationRow.priority_date, 'ddd mmm yyyy', ' '));
        cy.get('[data-cy="date"] > p:nth-child(3)').should('contain', formatDate(allocationRow.expiry_date, 'ddd mmm yyyy', ' '));
        cy.get('[data-cy="date"] > p:nth-child(4)').should('contain', formatDate(allocationRow.lic_status_date, 'ddd mmm yyyy', ' '));
        cy.get('[data-cy="quantity"]').should('contain', "1,234.0");
        cy.get('[data-cy="flag"]').should('contain', allocationRow.qty_flag);
        cy.get('[data-cy="type"] > div').should('have.class', allocationRow.lic_type);
        cy.get('[data-cy="type"] > div').should('contain', allocationRow.lic_type);
        cy.get('[data-cy="status"] > .q-icon').should('have.class', 'mdi-check-circle').and('have.class', 'text-green-5')
    })
    it('sets and resets filters', () => {
        cy.mount(Allocations, {
            props: {
                reportContent: reportData
            }
        });
        // check value exists before filtering
        cy.get('[data-cy="quantity"]').should('contain', "1,234.0");
        cy.get('.mdi-filter').click()
        cy.get('.q-checkbox__label').contains('Surface Water').click()
        cy.get('[data-cy="quantity"]').should('not.exist');
        cy.get('.q-checkbox__label').contains('Surface Water').click()
        cy.get('[data-cy="quantity"]').should('contain', "1,234.0");
        cy.get('.q-checkbox__label').contains('Application').click()
        cy.get('[data-cy="quantity"]').should('not.exist');
        cy.get('.q-checkbox__label').contains('Application').click();
        cy.get('.q-checkbox__label').contains('Agriculture').click();
        cy.get('[data-cy="quantity"]').should('not.exist');
        cy.get('.q-checkbox__label').contains('Agriculture').click();
        cy.get('[data-cy="quantity"]').should('contain', "1,234.0");
        cy.get('input[placeholder="Text Search"]').type('TESTING')
        cy.get('[data-cy="quantity"]').should('not.exist');
        cy.get('input[placeholder="Text Search"]').clear()
        cy.get('input[placeholder="Text Search"]').type('Cypress')
        cy.get('[data-cy="quantity"]').should('contain', "1,234.0");
        cy.get('span').contains('Reset Filters').click();
        cy.get('input[placeholder="Text Search"]').should('have.value', '');
    })
})
