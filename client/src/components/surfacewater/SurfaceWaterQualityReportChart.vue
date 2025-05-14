<template>
    <div class="surface-water-chart-container">
        <div class="chart-header text-h6 q-mb-md">
            {{ props.chartData.title }} ({{ props.chartData.units }})
        </div>
        <ChartLegend 
            :legend-list="[{
                color: 'steelblue',
                label: props.chartData.title
            }]"
        />
        <div :id="props.chartId"></div>
        <div
            v-if="showTooltip"
            class="surface-water-tooltip"
            :style="`top: ${tooltipPosition[1]}px; left: ${tooltipPosition[0]}px;`"
        >
            <q-card class="tooltip-content">
                <p class="tooltip-header">
                    <b>{{ tooltipData.date }}</b>
                </p>
                <p class="tooltip-row">
                    {{ props.chartData.title }} <b>{{ tooltipData.value ? tooltipData.value.toFixed(2) : 'No Data' }}</b>
                </p>
            </q-card>
        </div>
    </div>
</template>

<script setup>
import { monthAbbrList } from "@/utils/dateHelpers";
import { computed, onMounted, ref } from "vue";
import * as d3 from "d3";
import ChartLegend from "../streamflow/ChartLegend.vue";

const props = defineProps({
    chartData: {
        type: Object,
        default: () => {},
    },
    chartId: {
        type: String,
        default: "",
    },
});

const margin = { top: 20, right: 30, bottom: 50, left: 50 };
const width = ref();
const height = ref();
const svg = ref(null);
const g = ref();
const xAxisScale = ref();
const yAxisScale = ref();
const showTooltip = ref(false);
const tooltipData = ref(null);
const tooltipPosition = ref([0, 0]);

const minY = computed(() => {
    return d3.min(props.chartData.data.map(el => el.v));
});
const maxY = computed(() => {
    return d3.max(props.chartData.data.map(el => el.v));
});
// const chartLegendContents = computed(() => {
//     return [{
//         label: props.chartData
//     }]
// })

onMounted(async () => {
    width.value = 720 - margin.left - margin.right;
    height.value = 520 - margin.top - margin.bottom;

    // append the svg object to the body of the page
    svg.value = d3
        .select(`#${props.chartId}`)
        .append("svg")
        .attr("width", width.value + margin.left + margin.right)
        .attr("height", height.value + margin.top + margin.bottom);

    g.value = svg.value
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);
        
    init();
});

const init = () => {
    addAxes();
    addGridLines();
    addLine();
    addPoints();
}

/**
 * Includes hoverable points at each junction in the line
 */
const addPoints = () => {
    g.value
        .selectAll('.water-quality-point')
        .data(props.chartData.data)
        .enter()
        .append('circle')
        .attr('class', d => `water-quality-point`)
        .attr('cx', d => xAxisScale.value(new Date(d.d)))
        .attr('cy', d => yAxisScale.value(d.v))
        .attr("r", 3)
        .attr('visibility', d => {
            return d.v ? 'visible' : 'hidden'
        })
        .attr('fill', 'steelblue')
        .attr('stroke', 'steelblue')
        .attr('stroke-width', '2')
        .on('mousemove', (ev) => {
            d3.select(ev.target).attr('r', 6).attr('fill', 'white');
            addTooltip(ev);
        })
        .on('mouseleave', (ev) => {
            d3.select(ev.target).attr('r', 3).attr('fill', 'steelblue');
            removeTooltip();
        })
}

const addTooltip = (event) => {
    const hoverMonth = monthAbbrList[new Date(event.target.__data__.d).getUTCMonth()];
    const hoverDate = new Date(event.target.__data__.d).getUTCDate();
    const hoverYear = new Date(event.target.__data__.d).getUTCFullYear();

    tooltipData.value = {
        date: `${hoverMonth} ${hoverDate}, ${hoverYear}`,
        value: event.target.__data__.v
    }
    tooltipPosition.value = [
        event.pageX - 200,
        event.pageY - 100,
    ]
    showTooltip.value = true;
}

const removeTooltip = () => {
    showTooltip.value = false;
}

const addLine = () => {
    // Plot the area
    g.value
        .append("path")
        .datum(props.chartData.data)
        .attr("fill", "none")
        .attr("stroke", "steelblue")
        .attr("stroke-width", 1.5)
        .attr(
            "d",
            d3
                .line()
                .x(d => xAxisScale.value(new Date(d.d)))
                .y(d => yAxisScale.value(d.v))
                .defined(d => d.v !== null)
        );
}

const addGridLines = () => {
    // add grid lines
    g.value
        .append("g")
        .attr("class", "x axis-grid")
        .call(
            d3.axisBottom(xAxisScale.value)
            .tickSize(height.value)
            .ticks(6)
            .tickFormat("")
        );

    g.value
        .append("g")
        .attr("class", "y axis-grid")
        .call(
            d3.axisLeft(yAxisScale.value)
            .tickSize(-width.value)
            .tickFormat("")
        );
}

const addAxes = () => {
    // Add X axis
    xAxisScale.value = d3
        .scaleTime()
        .domain([new Date(props.chartData.data[0].d), new Date(props.chartData.data[props.chartData.data.length - 1].d)])
        .range([0, width.value])
        .nice();

    // Add Y axis label
    g.value
        .append("text")
        .attr("class", "text-capitalize")
        .attr("text-anchor", "end")
        .attr("fill", "#5d5e5d")
        .attr("y", 6)
        .attr("dx", "-15em")
        .attr("dy", "-3em")
        .attr("transform", "rotate(-90)")
        .text(`${props.chartData.units}`);

    g.value
        .append("g")
        .attr("transform", `translate(0, ${height.value})`)
        .call(
            d3
                .axisBottom(xAxisScale.value)
                .tickFormat(d3.timeFormat('%b %Y'))
                .ticks(6)
        );

    g.value
        .append('text')
        .attr('class', 'x axis-label')
        .attr("transform", `translate(${(width.value / 2) - margin.right}, ${height.value + 35})`)
        .attr("fill", "#5d5e5d")
        .text('Date')

    // Add Y axis
    yAxisScale.value = d3
        .scaleLinear()
        .domain([minY.value, maxY.value])
        .range([height.value, 0])
        .nice();

    g.value.append("g").call(d3.axisLeft(yAxisScale.value).ticks(3));
}
</script>

<style lang="scss">
.chart-header {
    display: flex;
    justify-content: center;
}

.surface-water-chart-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 3rem;
}

.surface-water-tooltip {
    position: absolute;
    background-color: rgba(255, 255, 255, 0.95);
    border: 1px solid $light-grey-accent;
    border-radius: 3px;
    display: flex;
    flex-direction: column;
    pointer-events: none;

    .tooltip-header {
        font-size: 18px;
        padding: 0.25em 1em;
    }

    .tooltip-row {
        padding: 0.25em 1em;
    }
}

.axis-grid {
    .domain {
        stroke: #ccc;
    }    
    line { 
        stroke: #ccc;
    }
}
</style>
