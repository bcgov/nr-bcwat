<template>
    <div>
        <h1 class="q-my-lg">Current and Future Hydrologic Variability</h1>
        <p>
            Modeled hydrologic variability and future characteristics derived from process based hydrology models from Pacific Climate Impacts Consortium
            (PCIC) and the University of Colorado (UC)
        </p>
        <p>
            The chart and table below summarize the daily output of Variable In ltration Capacity (VIC) hydrology models to describe potential past and future hydrologic variability in the
            watershed. Values should be used as estimations only. If the chart and table below have only 1976-2006 values, the data is from UC. If there are future predictions, the data is from
            PCIC.
        </p>
        <FutureHydrologicVariabilityBarChart
            :chart-data="props.reportContent.futureHydrologicVariability"
        />

        <FutureHydrologicVariabilityTabularData
            :table-data="
                props.reportContent.futureHydrologicVariability['1976']
            "
            year="1976"
            color-accent="#c694c3"
            color="#8f3d96"
        />
        <FutureHydrologicVariabilityTabularData
            :table-data="
                props.reportContent.futureHydrologicVariability['2011']
            "
            year="2011"
            color-accent="#7a85c1"
            color="#32429b"
        />
        <FutureHydrologicVariabilityTabularData
            :table-data="
                props.reportContent.futureHydrologicVariability['2041']
            "
            year="2041"
            color-accent="#95c8ec"
            color="#418ecc"
        />
         <FutureHydrologicVariabilityTabularData
            :table-data="
                props.reportContent.futureHydrologicVariability['2071']
            "
            year="2071"
            color-accent="#89d4e3"
            color="#13bdd5"
        />
        <hr class="q-my-xl" />
    </div>
</template>

<script setup>
import FutureHydrologicVariabilityBarChart from "@/components/watershed/report/FutureHydrologicVariabilityBarChart.vue";
import FutureHydrologicVariabilityTabularData from "@/components/watershed/report/FutureHydrologicVariabilityTabularData.vue";

const props = defineProps({
    reportContent: {
        type: Object,
        default: () => {},
    }
});

</script>

<style lang="scss">
.hydrologic-map-legend {
    align-items: center;
    background-color: $light-grey-accent;
    border: 1px solid grey;
    display: flex;
    flex-wrap: wrap;
    padding: 1em;

    svg {
        max-height: 30px;
        margin-right: 1em;
    }

    div {
        align-items: center;
        display: flex;
        flex-direction: row;
    }

    .legend-circle {
        border-radius: 50%;
        margin-left: 1em;
        margin-right: 0.5em;
        height: 20px;
        width: 20px;
    }
}
</style>
