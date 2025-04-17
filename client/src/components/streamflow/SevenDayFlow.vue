<template>
    <div class="seven-day-area">
        <div class="seven-day-header">
            <q-select 
                :model-value="yearlyData"
                class="yearly-input"
                :options="yearlyDataOptions"
                label="Select"
                hint="Add yearly data"
                clearable
                multiple
                dense
                outline
                @update:model-value="(newval) => {
                    if(!newval){
                        yearlyData = []
                    } else {
                        yearlyData = newval
                    }
                    updateChartLegendContents()
                }"
            />
            <div class="chart-legend">
                <ChartLegend 
                    :legend-list="chartLegendArray"
                />
            </div>
        </div>

        <div 
            id="streamflow-chart-container"
        >
            <div class="svg-wrap">
                <div class="d3-chart">
                    <g class="chart-elements" />
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import * as d3 from "d3";
import sevenDay from "@/constants/sevenDay.json";
import { ref, computed, onMounted } from 'vue';
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

const chartLegendArray = ref([]);
const yearlyData = ref([]);
const colors = ref(null);

// chart sizing
const margin = {
    top: 10,
    right: 50,
    bottom: 35,
    left: 50,
};
let width = 400;
let height = 200;

// chart-specific variables:
const formattedChartData = ref();
const svgWrap = ref();
const svgEl = ref();
const svg = ref();
const chartStart = ref();
const chartEnd = ref();
const scaleX = ref();
const scaleY = ref();
const yMax = ref();
const yMin = ref();

/**
 * determine which years of data are available for the point
 */ 
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

onMounted(() => {
    window.addEventListener("resize", updateChart);
    updateChartLegendContents();
});

/**
 * handler for fetching a color from the pre-defined color scale and 
 * creating a list of legend items
 */ 
const updateChartLegendContents = () => {
    chartLegendArray.value = [];
    colors.value = colors.value || d3.scaleOrdinal(colorScale);
    yearlyData.value.forEach((year, idx) => {
        chartLegendArray.value.push({
            label: year,
            color: colors.value(idx)
        })
    });
    // add the historical label and color
    chartLegendArray.value.push({
        label: 'Historical',
        color: '#ddd'
    })
    chartLegendArray.value.sort((a, b) => a.label - b.label);
};

/**
 * calls the component functions to build the chart and set its data
 */
const init = () => {
    formatChartData(sevenDay);

    svgWrap.value = document.querySelector('.svg-wrap');
    svgEl.value = svgWrap.value.querySelector('svg');
    svg.value = d3.select(svgEl.value)
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append('g')
        .attr('class', 'g-els')
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    if (svgWrap.value) {
        width = svgWrap.value.clientWidth - margin.left - margin.right;
        height = svgWrap.value.clientHeight - margin.top - margin.bottom;
    }

    // set the data from selections to align with the chart range
    setDateRanges();

    // build the chart axes
    setAxisX();
    setAxisY();

    // add clip-path element
    const defs = svg.value.append('defs');
    defs.append('clipPath')
        .attr('id', 'streamflow-box-clip')
        .append('rect')
        .attr('width', width)
        .attr('height', height);

    addXaxis();
    addYaxis();
}

const addXaxis = () => {
    
}

const addYaxis = () => {

}

const formatChartData = (data) => {
    try{
        formattedChartData.value = data.map(d => {
            return {
                d: new Date(d),
                v: d.v
            }
        })
    } catch (e) {
        formattedChartData.value = [];
    }
}

const setDateRanges = () => {
    chartStart.value = new Date().setFullYear(new Date().getUTCFullYear(), 0, 1);
    chartEnd.value = new Date().setFullYear(new Date().getUTCFullYear() + 1, 0, 1);
}

const setAxisX = () => {
    // set x-axis scale
    scaleX.value = d3.scaleTime()
        .domain([chartStart.value, chartEnd.value])
        .range([0, width])
}

const setAxisY = () => {
    const valsToCheck = [d3.max(formattedChartData.value.map(d => d.v))];

    yMax.value = d3.max(valsToCheck);
    yMax.value *= 1.10;
    yMin.value = 0;

    // Y axis
    scaleY.value = d3.scaleSymlog()
        .range([height, 0])
        .domain([0, yMax.value]);

}


/**
 * Ensures the chart dimensions and content are resized when the windows is adjusted
 */
const updateChart = () => {
    // timeout catches some potential rendering issues.
    setTimeout(() => {
        init();
    }, 100)
}
</script>

<style lang="scss" scoped>
.seven-day-header {
    display: flex;
    align-items: center;
    justify-content: space-between;

    .yearly-input {
        width: 30%;
    }

    .chart-legend {
        width: 70%;
        margin: 0 2rem;
    }
}

.seven-day-area{
    height: 100%;
}

#streamflow-chart-container {
    height: 90%;
}

.svg-wrap {
    height: 100%;

    .d3-chart {
        width: 100%;
        height: 100%;
    }
}

// elements clipped by the clip-path rectangle
.streamflow-clipped {
    clip-path: url('#streamflow-box-clip');
}
</style>
