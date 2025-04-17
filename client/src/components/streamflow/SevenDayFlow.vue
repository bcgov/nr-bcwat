<template>
    <q-select 
        v-model="yearlyData"
        :options="yearlyDataOptions"
        multiple
        dense
        outline
    />
    {{ chartLegendContents }}
    <ChartLegend 
        :legend-list="chartLegendContents"
    />
</template>

<script setup>
import * as d3 from "d3";
import { ref, computed } from 'vue';
import ChartLegend from "./ChartLegend.vue";

const props = defineProps({
    selectedPoint: {
        type: Object,
        default: () => {},
    }
});

const colorScale = [
    '#2196F3',
    '#FF9800',
    '#4CAF50',
    '#9C27B0',
    '#795548',
    '#FF80AB',
    '#00897B',
    '#AFB42B',
    '#00BCD4',
];

const yearlyData = ref([]);
const colors = ref(null);

// determine which years of data are available for the point
const yearlyDataOptions = computed(() => {
    if(props.selectedPoint){
        const arr = [];
        for(let i = JSON.parse(props.selectedPoint.yr)[0]; i <= JSON.parse(props.selectedPoint.yr)[1]; i++){
            arr.push(i);
        }
        return arr;
    }
    return [];
});

const chartLegendContents = computed(() => {
    const legendArr = [];
    colors.value = colors.value || d3.scaleOrdinal(colorScale);
    yearlyDataOptions.value.forEach(year => {
        legendArr.push({
            label: year,
            color: colors.value(1)
        })
    });
});
</script>
