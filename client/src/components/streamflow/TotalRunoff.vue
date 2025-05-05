
<template>
    <h3>Total Runoff ({{ props.startEndRange[0] }} - {{ props.startEndRange[1] }})</h3>
    <div id="total-runoff-chart-container">
        <div class="svg-wrap-tr">
            <svg class="d3-chart-tr">
                <!-- d3 chart content renders here -->
            </svg>
        </div>
    </div>
</template>

<script setup>
import * as d3 from "d3";
import { monthAbbrList } from '@/constants/dateHelpers.js';
import { onMounted, ref, watch } from "vue";

const props = defineProps({
    data: {
        type: Array,
        default: () => [],
    },
    startEndRange: {
        type: Array,
        required: true,
    }
});

const loading = ref(false);
const formattedChartData = ref([]);

// chart variables
const svgWrap = ref();
const svgEl = ref();
const svg = ref();
const g = ref();
const yMax = ref(0);
const yMin = ref(0);

// chart scaling
const xScale = ref();
const yScale = ref();

// chart constants 
const width = 600;
const height = 300;
const margin = {
    left: 50,
    right: 50,
    top: 10,
    bottom: 50
};

watch(() => props.startEndRange, () => {
    processData(props.data, props.startEndRange);
    initTotalRunoff();
})

onMounted(() => {
    loading.value = true;
    processData(props.data, props.startEndRange);
    initTotalRunoff();
    loading.value = false;
});

const initTotalRunoff = () => {
    if (svg.value) {
        d3.selectAll('.g-els.tr').remove();
    }

    svgWrap.value = document.querySelector('.svg-wrap-tr');
    svgEl.value = svgWrap.value.querySelector('svg');
    svg.value = d3.select(svgEl.value)
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .attr("transform", `translate(${margin.left}, ${margin.top})`);

    g.value = svg.value.append('g')
        .attr('class', 'g-els tr')
        .attr("transform", `translate(${margin.left}, ${margin.top})`);

    // add clip-path element - removing content outside the chart
    const defs = g.value.append('defs');
    defs.append('clipPath')
        .attr('id', 'total-runoff-box-clip')
        .append('rect')
        .attr('width', width)
        .attr('height', height);

    setAxes();
    addAxes();
};

const addAxes = (scale = { x: xScale.value, y: yScale.value }) => {
    // x axis labels and lower axis line
    g.value.append('g')
        .attr('class', 'x axis')
        .call(
            d3.axisBottom(scale.x)
                .tickFormat(d => `${d}%`)
        )
        .attr('transform', `translate(0, ${height + 0})`)

    // x axis labels and lower axis line
    g.value.append('g')
        .attr('class', 'y axis')
        .call(
            d3.axisLeft(scale.y)
                .ticks(3)
        )
        .attr('transform', `translate(0, 0)`)

    g.value.append('text')
        .attr('class', 'y axis-label')
        .attr("transform", `translate(-40, ${height / 1.5})rotate(-90)`)
        .text('Flow (m³/s)')
}

const setAxes = () => {
    // set x-axis scale
    xScale.value = d3.scaleLinear()
        .domain([0, 100])
        .range([0, width])

    // set y-axis scale
    yMax.value = d3.max(formattedChartData.value.map(el => el.exceedance));
    yMax.value *= 1.10;

    // Y axis
    yScale.value = d3.scaleSymlog()
        .range([height, 0])
        .domain([0, yMax.value]);
}

/**
 * handles the provided data and calculates the exceedance for the currently
 * selected range of data. 
 * 
 * @param dataToProcess - Array of all of the data returned by the API
 * @param range - start and end month array. eg. ['Jan', 'Dec']
 */
const processData = (dataToProcess, range) => {
    const start = monthAbbrList.indexOf(range[0])
    const end = monthAbbrList.indexOf(range[1])

    const dataInRange = dataToProcess.filter(el => {
        const monthIdx = new Date(el.d).getMonth();
        return monthIdx >= start && monthIdx <= end
    })

    formattedChartData.value = calculateExceedance(dataInRange.sort((a, b) => b.v - a.v))
}

const calculateExceedance = (sortedDescendingArray) => {
    const N = sortedDescendingArray.length;
    return sortedDescendingArray.map((value, i) => {
        return {
            value: value.v,
            exceedance: ((i + 1) / N) * 100
        }
    });
}
</script>

<style lang="scss">
// elements clipped by the clip-path rectangle
.total-runoff-clipped {
    clip-path: url('#total-runoff-box-clip');
}
</style>
