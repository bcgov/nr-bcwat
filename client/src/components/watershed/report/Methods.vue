<template>
    <div>
        <h1 class="q-my-lg">Methods</h1>
        <h5>Modeling</h5>
        <p>
            The hydrologic model driving the BC Water Tool was produced
            following similar methods to those described in:
        </p>

        <p>
            Chapman A, Kerr B, Wilford D (2018) A water allocation
            decision-support model and tool for predictions in ungauged basins
            in northeast British Columbia. J Am Water Resour Assoc 54 (3):
            676–693.
            <a href="https://doi.org/10.1111/1752-1688.12643" target="_blank">
                https://doi.org/10.1111/1752-1688.12643
            </a>
        </p>

        <p>The BC Water Tool uses climate drivers from:</p>

        <p>
            ClimateWNA v4.72 Normal {{ regionMethodsData.climateDriverYears }}
        </p>

        <p>
            Calibration and validation was performed using hydrometric records
            which were selected based on length of record, seasonality, and
            other characteristics.
        </p>

        <p>Hydrometric stations used: {{ regionMethodsData.numWatersheds }}</p>

        <p>Annual model performance:</p>

        <div class="methods-box">
            <p>Mean Error: {{ regionMethodsData.meanError }}%</p>
            <p>Median Error: {{ regionMethodsData.medianError }}%</p>
            <p>
                Mean Absolute Error: {{ regionMethodsData.meanAbsoluteError }}%
            </p>
            <p>
                % of stations within +/- 20%:
                {{ regionMethodsData.watershedsWithin20Percent }}%
            </p>
        </div>
    </div>
</template>

<script setup>
import { FS_HYDROLOGY_MODEL } from "@/constants/model-information.js";
import { computed } from 'vue';

const props = defineProps({
    reportContent:  {
        type: Object,
        default: () => {},
    }
});

const regionMethodsData = computed(() => {
    if (props.reportContent.regionalId == '1') {
        return FS_HYDROLOGY_MODEL['SWP'];
    } else if (props.reportContent.regionalId == '2') {
        return FS_HYDROLOGY_MODEL['NWP'];
    } else if (props.reportContent.regionalId == '3') {
        return FS_HYDROLOGY_MODEL['Cariboo'];
    } else if (props.reportContent.regionalId == '4') {
        return FS_HYDROLOGY_MODEL['KWT'];
    } else if (props.reportContent.regionalId == '5') {
        return FS_HYDROLOGY_MODEL['NWWT'];
    } else if (props.reportContent.regionalId == '6') {
        return FS_HYDROLOGY_MODEL['OWT'];
    } else {
        return FS_HYDROLOGY_MODEL['NEWT'];
    }
})
</script>

<style lang="scss">
.methods-box {
    border-radius: 5px;
    box-shadow: 2px 2px 2px 4px rgba(0, 0, 0, 0.1);
    padding: 1em;
    margin-bottom: 1em;
}
</style>
