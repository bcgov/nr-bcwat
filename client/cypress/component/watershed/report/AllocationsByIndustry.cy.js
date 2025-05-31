import AllocationsByIndustry from '@/components/watershed/report/AllocationsByIndustry.vue';
import watershedReport from '@/constants/watershedReport.json';

const reportData = { allocationsByIndustry: watershedReport.allocationsByIndustry };

describe('<AllocationsByIndustry />', () => {
    it('mounts successfully', () => {
        cy.mount(AllocationsByIndustry, {
            props: {
                reportContent: reportData
            }
        })
    });
});
