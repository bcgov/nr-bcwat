import AllocationsByIndustry from '@/components/watershed/report/AllocationsByIndustry.vue';

const reportData = { allocationsByIndustry: {
        "Agriculture": {
            "sw_long": 11,
            "sw_short": 12,
            "gw_long": 13,
            "gw_short": 14
        },
        "Commercial": {
            "sw_long": 21,
            "sw_short": 22,
            "gw_long": 23,
            "gw_short": 24
        },
        "Domestic": {
            "sw_long": 31,
            "sw_short": 32,
            "gw_long": 33,
            "gw_short": 34
        },
        "Municipal": {
            "sw_long": 41,
            "sw_short": 42,
            "gw_long": 43,
            "gw_short": 44
        },
        "Oil & Gas": {
            "sw_long": 50,
            "sw_short": 50,
            "gw_long": 50,
            "gw_short": 50
        },
        "Other": {
            "sw_long": 61,
            "sw_short": 62,
            "gw_long": 63,
            "gw_short": 64
        },
        "Power": {
            "sw_long": 71,
            "sw_short": 72,
            "gw_long": 73,
            "gw_short": 74
        },
        "Storage": {
            "sw_long": 81,
            "sw_short": 82,
            "gw_long": 83,
            "gw_short": 84
        }
    }
};

describe('<AllocationsByIndustry />', () => {
    it('mounts and loads table data', () => {
        cy.mount(AllocationsByIndustry, {
            props: {
                reportContent: reportData
            }
        })
        Object.keys(reportData.allocationsByIndustry).forEach((key, idx) => {
            // offset for the header rows of the table plus 1-index
            const headerRowsCount = 3;
            cy.get(`.allocation-industry-table > tbody > tr:nth-child(${idx + headerRowsCount}) > td`).should('contain', key)
            Object.keys(reportData.allocationsByIndustry[key]).forEach((allocationKey, allocationIdx) => {
                cy.get(`.allocation-industry-table > tbody > tr:nth-child(${idx + headerRowsCount}) > td`).should('contain', reportData.allocationsByIndustry[key][allocationKey])
            });
        })
    });
});
