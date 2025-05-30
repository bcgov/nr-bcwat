import Allocations from "@/components/watershed/report/Allocations.vue";
import watershedReport from '@/constants/watershedReport.json';

const reportData = watershedReport;

describe('<Allocations />', () => {
    it('laods and renders content', () => {
        cy.mount(Allocations, {
            props: {
                reportContent: reportData
            }
        }).then(component => {
            console.log(component.component)
        })
    })
})
