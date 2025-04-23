<template>
    <div>
        <h1>Monthly Water Supply and Demand - {{ reportContent.overview.watershedName }}</h1>
        <p>
            Hydrologic models have been developed to produce estimates of mean
            monthly flows. The Province of BC’s Environmental Flow Needs Policy
            has been applied to these estimates, identifying risk management
            levels to support water management decisions. Information on active
            water licences and approvals (collectively, ‘allocations’) in the
            watershed have been extracted and summarized from government
            databases and integrated with the hydrology model data and risk
            management level calculations, to account for the volume of water
            already allocated.
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
        <div class="monthly-hydrology-container">
            <MonthlyHydrologyLegend :mad="reportContent.queryMonthlyHydrology.meanAnnualDischarge"/>
            <MonthlyHydrologyChart
                :chart-data="reportContent.queryMonthlyHydrology"
                chart-id="monthly-chart"    
            />
        </div>
        
        <MonthlyHydrologyTable
            :monthly-hydrology="reportContent.queryMonthlyHydrology"
            :month-abbr-list="monthAbbrList"
        />

        <hr class="q-my-xl">
        <h1 class="q-mb-md">Monthly Water Supply and Demand - {{ reportContent.overview.watershedName }} (Downstream)</h1>
        <p>
            Similar to the previous section, which described the water supply and demand for the location that you selected, this section describes the water supply and demand for the downstream basin. The hydrology model and risk management calculations are the exact same, but the calculation logic for existing allocations is different, taking into account non-consumptive, or ‘flow-through’ water rights.
        </p>

        <div class="monthly-hydrology-container">
            <MonthlyHydrologyLegend :mad="reportContent.downstreamMonthlyHydrology.meanAnnualDischarge"/>
            <MonthlyHydrologyChart
                :chart-data="reportContent.downstreamMonthlyHydrology"
                chart-id="monthly-chart-downstream"    
            />
        </div>
        
        <MonthlyHydrologyTable
            :monthly-hydrology="reportContent.downstreamMonthlyHydrology"
            :month-abbr-list="monthAbbrList"
        />
        <hr />
    </div>
</template>

<script setup>
import MonthlyHydrologyChart from "@/components/watershed/report/MonthlyHydrologyChart.vue";
import MonthlyHydrologyLegend from "@/components/watershed/report/MonthlyHydrologyLegend.vue";
import MonthlyHydrologyTable from "@/components/watershed/report/MonthlyHydrologyTable.vue";

const props = defineProps({
    reportContent: {
        type: Object,
        default: () => {},
    },
});

const monthAbbrList = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
];

</script>

<style lang="scss">
.monthly-hydrology-container {
    display: flex;
}
</style>
