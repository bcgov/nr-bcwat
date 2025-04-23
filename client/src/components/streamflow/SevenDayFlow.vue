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
                    yearlyData = newval ? newval : []
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
                <svg class="d3-chart">
                    <!-- d3 chart content renders here -->
                </svg>
            </div>
        </div>

        <div 
            class="seven-day-tooltip"
            :style="`left: ${tooltipPosition[0]}px; top: ${tooltipPosition[1]}px; `"
        >
            {{ tooltipText }}AHG
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

// tooltip variables:
const tooltipText = ref([]);
const tooltipPosition = ref([]);

// chart-specific variables:
const formattedChartData = ref();
const svgWrap = ref();
const svgEl = ref();
const svg = ref();
const g = ref();
const chartStart = ref();
const chartEnd = ref();
const innerBars = ref();
const outerBars = ref();
const medianLine = ref();
const historicalLines = ref([]);
const scaleX = ref();
const scaleY = ref();
const yMax = ref();
const yMin = ref();
const gAxisY = ref();
const gGridX = ref();
const gGridY = ref();

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
    updateChart();
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
    if (svg.value) {
        svg.value.selectAll('*').remove();
    }

    // set the data from selections to align with the chart range
    setDateRanges();

    formatChartData(sevenDay);

    svgWrap.value = document.querySelector('.svg-wrap');
    svgEl.value = svgWrap.value.querySelector('svg');
    svg.value = d3.select(svgEl.value)
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        
    g.value = svg.value.append('g')
        .attr('class', 'g-els')
        .attr("transform", `translate(${margin.left}, ${margin.top})`);

    if (svgWrap.value) {
        width = svgWrap.value.clientWidth - margin.left - margin.right;
        height = svgWrap.value.clientHeight - margin.top - margin.bottom;
    }

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
    addChartData();

    addHoverEvents();
}

/**
 * When the mouse leaves the svg, set the text to blank. This hides the tooltip
 */
const tooltipMouseOut = () => {
    tooltipText.value = "";
};

/**
 * When the mouse moves over the svg, get the value the user is hovering over and display it in a tooltip
 * @param {*} event the mouse event containing the text to display and position to display it at
 */
const tooltipMouseMove = (event) => {
    tooltipPosition.value = [event.pageX - 50, event.pageY];
    const [gX, gY] = d3.pointer(event, g.value.node());
    
};

/**
 * Add mouse events for the chart tooltip and hover, if applicable
 */
const addHoverEvents = () => {
    svg.value.on("mousemove", (ev) => tooltipMouseMove(ev));
    svg.value.on("mouseout", tooltipMouseOut);
    // TODO add hover line or date indicator 
}

const addOuterBars = () => {
    outerBars.value = svg.value.selectAll('.bar.outer')
        .data(formattedChartData.value)
        .enter().append('rect')
        .attr("fill", "#dde3e3")
        .attr('class', 'sdf bar outer')
        .attr('x', d => scaleX.value(d.d))
        .attr('y', d => scaleY.value(d.max))
        .attr('width', d => width / formattedChartData.value.length + 0.5)
        .attr('height', d => Math.abs(scaleY.value(d.max) - scaleY.value(d.min)));
}

const addInnerbars = () => {
    innerBars.value = svg.value.selectAll('.bar.inner')
        .data(formattedChartData.value)
        .enter().append('rect')
        .attr("fill", "#ccd5d5")
        .attr('class', 'sdf bar inner')
        .attr('x', d => scaleX.value(d.d))
        .attr('y', d => scaleY.value(d.p75))
        .attr('width', d => width / formattedChartData.value.length + 0.5)
        .attr('height', d => Math.abs(scaleY.value(d.p75) - scaleY.value(d.p25)));
}

const addMedianLine = () => {
    medianLine.value = svg.value
        .append('path')
        .datum(formattedChartData.value)
        .attr('fill', 'none')
        .attr('stroke', '#999999')
        .attr('stroke-width', 2)
        .attr('class', 'sdf line median')
        .attr('d', d3.line()
            .x(d => scaleX.value(d.d))
            .y(d => scaleY.value(d.p50))
            .defined(d => d.p50 !== null && d.p50 !== NaN)
        )
}

const addChartData = (year) => {
    addOuterBars();
    addInnerbars();
    addMedianLine();
}

const addXaxis = (scale = scaleX.value) => {
    if(gGridX.value) svg.value.selectAll('.axis-grid').remove();
    gGridX.value = svg.value.append('g')
        .attr('class', 'x axis-grid')
        .call(
            d3.axisBottom(scale)
                .tickSize(height)
                .tickFormat(d3.timeFormat('%B'))
                .ticks(12)
        )
}

const addYaxis = (scale = scaleY.value) => {
    if(gAxisY.value) gAxisY.value.remove();
    gAxisY.value = svg.value.append("g")
        .call(
            d3.axisLeft(scale)
        );

    // adds the y-axis grid lines to the chart.
    const yAxisGrid = d3.axisLeft(scale)
        .tickSize(-width)
                .tickFormat('')
                .ticks(5)

    if (gGridY.value) gGridY.value.remove();
    gGridY.value = svg.value.append('g')
        .attr('class', 'y axis-grid')
        .call(yAxisGrid);
}

const formatChartData = (data) => {
    try{
        formattedChartData.value = data.map(el => {
            return {
                d: new Date(new Date(chartStart.value).getUTCFullYear(), 0, el.d),
                max: el.max,
                min: el.min,
                p25: el.p25,
                p50: el.p50,
                p75: el.p75,
            }
        });
    } catch (e) {
        formattedChartData.value = [];
    }
}

const setDateRanges = () => {
    chartStart.value = new Date().setFullYear(new Date().getUTCFullYear() - 1, 0, 1);
    chartEnd.value = new Date().setFullYear(new Date().getUTCFullYear(), 0, -1);
}

const setAxisX = () => {
    // set x-axis scale
    scaleX.value = d3.scaleTime()
        .domain([chartStart.value, chartEnd.value])
        .range([0, width])
        .nice();
}

const setAxisY = () => {
    const valsToCheck = [d3.max(formattedChartData.value.map(d => {d.max}))];

    yMax.value = d3.max(valsToCheck);
    yMax.value *= 1.10;
    yMin.value = 0;

    // Y axis
    scaleY.value = d3.scaleLinear()
        .range([height, 0])
        .domain([0, 500]); // set to yMax
}

/**
 * Ensures the chart dimensions and content are resized when the windows is adjusted
 */
const updateChart = () => {
    // timeout catches some potential rendering issues.
    setTimeout(() => {
        init();
    })
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

.seven-day-tooltip {
    position: absolute;
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

.dashed{
   stroke-dasharray: 5,6;
}

.x.axis-grid {
    text {
        transform: translate(0, -5rem);
    }
}

.axis-grid {
    pointer-events: none;

    line {
        stroke: rgba(201, 201, 201, 0.75);
    }
    path {
        visibility: hidden;
    }
}

// elements clipped by the clip-path rectangle
.streamflow-clipped {
    clip-path: url('#streamflow-box-clip');
}
</style>
