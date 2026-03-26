<template>
    <div>
        <div class="report-break">
            <div :class="props.isReport ? 'report-section-header' : ''">
                <div class="monthly-hydrology-header">
                    <MapMarker class="q-mt-md" fill="#cc5207" />
                    <div class="text-h4 q-my-md">
                        Monthly Water Supply and Demand -
                        {{ reportContent.overview.watershedName }}
                    </div>
                </div>
            </div>
            <p>
                Hydrologic models<NoteLink :note-number="6" /> have been developed
                to produce estimates of mean monthly flows. The Province of BC’s
                <i>Environmental Flow Needs Policy</i
                ><NoteLink :note-number="7" /> has been applied to these estimates,
                identifying risk management levels<NoteLink :note-number="8" /> to
                support water management decisions. Information on active water
                licences and approvals (collectively, ‘allocations’) in the
                watershed have been extracted and summarized from government
                databases<NoteLink :note-number="9" />
                and integrated with the hydrology model data and risk management
                level calculations, to account for the volume of water already
                allocated.
            </p>
            <p>
                In the chart below, the height of each column represents the mean
                monthly discharge - the long term, estimated average flow for that
                month of the year. The dark, medium, and light blue areas of the
                columns show the potential amount of water allocations within each
                risk management level. When allocations exist in the watershed, a
                red box hangs down from the top of each column to represent the
                volume of existing allocations in the context of mean monthly
                supply. The table below corresponds to the data shown on the chart.
            </p>
            <div class="hydrology-chart-container">
                <MonthlyHydrologyLegend
                    :mad="reportContent.queryMonthlyHydrology.meanAnnualDischarge"
                    :is-report="props.isReport"
                />
                <div class="flex">
                    <MonthlyHydrologyChart
                        :chart-data="reportContent.queryMonthlyHydrology"
                        chart-id="monthly-chart"
                        :mad="reportContent.queryMonthlyHydrology.meanAnnualDischarge"
                        :is-report="props.isReport"
                    />
                </div>
            </div>
            <div class="report-break">
                <MonthlyHydrologyTable
                    :monthly-hydrology="reportContent.queryMonthlyHydrology"
                    :is-report="props.isReport"
                />
            </div>
        </div>
        <q-separator class="q-my-xl" />

        <div class="report-break">
            <div :class="props.isReport ? 'report-section-header' : ''">
                <div class="monthly-hydrology-header">
                    <MapMarker class="q-mt-md" fill="#1e1436" />
                    <div class="text-h4 q-my-md">
                        Monthly Water Supply and Demand -
                        {{ reportContent.overview.mgmt_name }}
                    </div>
                </div>
            </div>
            <p>
                Similar to the previous section, which described the water supply
                and demand for the location that you selected, this section
                describes the water supply and demand for the downstream basin. The
                hydrology model and risk management calculations are the exact same,
                but the calculation logic for existing allocations is different,
                taking into account non-consumptive, or ‘flow-through’ water
                rights.<NoteLink :note-number="9" />
            </p>

            <div class="hydrology-chart-container">
                <MonthlyHydrologyLegend
                    :mad="reportContent.downstreamMonthlyHydrology.meanAnnualDischarge"
                    :is-report="props.isReport"
                />
                <div class="flex">
                    <MonthlyHydrologyChart
                        :chart-data="reportContent.downstreamMonthlyHydrology"
                        chart-id="monthly-chart-downstream"
                        :mad="reportContent.downstreamMonthlyHydrology.meanAnnualDischarge"
                        :is-report="props.isReport"
                    />
                </div>
            </div>

            <MonthlyHydrologyTable
                :monthly-hydrology="reportContent.downstreamMonthlyHydrology"
                :is-report="props.isReport"
            />
        </div>
        <q-separator class="q-my-xl" />
    </div>
</template>

<script setup>
import MapMarker from "@/components/watershed/report/MapMarker.vue";
import MonthlyHydrologyChart from "@/components/watershed/report/MonthlyHydrologyChart.vue";
import MonthlyHydrologyLegend from "@/components/watershed/report/MonthlyHydrologyLegend.vue";
import MonthlyHydrologyTable from "@/components/watershed/report/MonthlyHydrologyTable.vue";
import { waitForElementToExist } from "@/utils/chartHelpers.js";
import NoteLink from "@/components/watershed/report/NoteLink.vue";
import { onMounted } from "vue";

const props = defineProps({
    reportContent: {
        type: Object,
        default: () => {},
    },
    isReport: {
        type: Boolean,
        default: false,
    }
});

onMounted(async () => {
    // functionality to ensure that the charts are loaded as expected before PDF generation
    try {
        let monthlyHydrologyLoaded = false;
        let monthlyHydrologyDownstreamLoaded = false;
        await waitForElementToExist('#monthly-chart').then(() => {
            monthlyHydrologyLoaded = true;
        });
        await waitForElementToExist('#monthly-chart-downstream').then(() => {
            monthlyHydrologyDownstreamLoaded = true;
        });
        if (monthlyHydrologyLoaded && monthlyHydrologyDownstreamLoaded) {
            document.monthlyHydrologyLoaded = true;
        }
    } catch (e) {
        console.error('Error loading Monthly Hydrology charts', e);
    }
});
</script>

<style lang="scss" scoped>
.report-break {
    page-break-before: always;
}

.monthly-hydrology-header {
    align-items: center;
    display: grid;
    grid-template-columns: 50px 1fr;
    margin-bottom: 1em;
    
    svg {
        height: 50px;
    }
}

.hydrology-chart-container {
    display: flex;
    justify-content: center;
}
</style>
