<template>
    <div>
        <h1 class="q-mb-lg">Climate</h1>
        <p>
            The climate of the Halden Creek watershed has been characterized
            using gridded climate models. These models have been used to
            calculate long term average temperature, rain and snow
            accumulations. The timing and amount of precipitation is a strong
            indicator of water availability, and the state it falls in (rain or
            snow) determines what happens when it reaches the ground - whether
            it accumulates and melts when temperatures warm, or infiltrates and
            runs off rapidly after reaching the ground. Three estimates of
            future climate for the 2041-2070 time period have been assessed and
            used to illustrate a range of potential future conditions. The
            shaded areas on each chart show a range of future conditions, and
            the relationship with the solid line (showing the historical
            average) helps understand at what time of the year the temperature,
            precipitation, and precipitation as snow may be different.
        </p>

        <ClimateChart
            :chart-data="props.reportContent.climateChartData.temperature"
            chart-id="temperature"
            area-color="#f4cab5"
            line-color="#f06825"
        />

        <ClimateChart
            :chart-data="props.reportContent.climateChartData.precipitation"
            chart-id="precipitation"
            area-color="#add8e6"
            line-color="#42a5f5"
        />

        <ClimateChart
            :chart-data="props.reportContent.climateChartData.snow"
            chart-id="snow"
            area-color="#bebebe"
            line-color="#474748"
        />

        <hr class="q-my-xl" />
    </div>
</template>

<script setup>
import ClimateChart from "@/components/watershed/report/ClimateChart.vue";
const props = defineProps({
    reportContent: {
        type: Object,
        default: () => {},
    },
});
</script>
