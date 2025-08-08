<template>
    <div class="report-break">
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
            ClimateWNA v4.72 Normal {{ FS_HYDROLOGY_MODEL.climateDriverYears }}
        </p>

        <p>
            Calibration and validation was performed using hydrometric records
            which were selected based on length of record, seasonality, and
            other characteristics.
        </p>

        <p>Hydrometric stations used: {{ FS_HYDROLOGY_MODEL.numWatersheds }}</p>

        <p>Annual model performance:</p>

        <div class="methods-box">
            <p>Mean Error: {{ FS_HYDROLOGY_MODEL.meanError }}%</p>
            <p>Median Error: {{ FS_HYDROLOGY_MODEL.medianError }}%</p>
            <p>
                Mean Absolute Error: {{ FS_HYDROLOGY_MODEL.meanAbsoluteError }}%
            </p>
            <p>
                % of stations within +/- 20%:
                {{ FS_HYDROLOGY_MODEL.watershedsWithin20Percent }}%
            </p>
        </div>
    </div>
</template>

<script setup>
import { FS_HYDROLOGY_MODEL } from "@/constants/model-information.js";
</script>

<style lang="scss">
.methods-box {
    border-radius: 5px;
    box-shadow: 2px 2px 2px 4px rgba(0, 0, 0, 0.1);
    padding: 1em;
    margin-bottom: 1em;
}
</style>
