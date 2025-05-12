<template>
    <div>
        <div :id="props.chartId"></div>
        <div
            v-if="tooltipData"
            class="watershed-report-tooltip hydrologic-line-tooltip"
            :style="`top: ${tooltipPosition[1]}px; left: ${tooltipPosition[0]}px;`"
        >
            <p>
                <b>{{ monthAbbrList[tooltipData.date] }}</b>
            </p>
            <p>
                {{ props.chartType }} <b>{{ tooltipData.value.toFixed(2) }}</b>
            </p>
        </div>
    </div>
</template>

<script setup>
import { monthAbbrList } from "@/utils/dateHelpers";
import { computed, onMounted, ref } from "vue";
import * as d3 from "d3";

const props = defineProps({
    chartData: {
        type: Object,
        default: () => {},
    },
    chartId: {
        type: String,
        default: "",
    },
    chartType: {
        type: String,
        default: "",
    },
});

const margin = { top: 20, right: 10, bottom: 30, left: 30 };
const width = ref();
const height = ref();
const svg = ref(null);
const g = ref();
const xAxisScale = ref();
const tooltipData = ref(null);
const tooltipPosition = ref([0, 0]);

const minY = computed(() => {
    return Math.min(...props.chartData);
});
const maxY = computed(() => {
    return Math.max(...props.chartData);
});

onMounted(async () => {
    width.value = 220 - margin.left - margin.right;
    height.value = 120 - margin.top - margin.bottom;

    // append the svg object to the body of the page
    svg.value = d3
        .select(`#${props.chartId}`)
        .append("svg")
        .attr("width", width.value + margin.left + margin.right)
        .attr("height", height.value + margin.top + margin.bottom);

    g.value = svg.value
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    // Add X axis
    xAxisScale.value = d3
        .scaleTime()
        .domain([0, 11])
        .range([1, width.value - margin.right]);
    g.value
        .append("g")
        .attr("transform", `translate(0, ${height.value})`)
        .call(
            d3
                .axisBottom(xAxisScale.value)
                .tickFormat((_, i) => monthAbbrList[i][0])
        );

    // Add Y axis
    const y = d3
        .scaleLinear()
        .domain([minY.value, maxY.value])
        .range([height.value, 0]);
    g.value.append("g").call(d3.axisLeft(y).ticks(3));

    // Plot the area
    g.value
        .append("path")
        .datum(props.chartData)
        .attr("fill", "none")
        .attr("stroke", 'steelblue')
        .attr("stroke-width", 1.5)
        .attr(
            "d",
            d3
                .line()
                .x((_, idx) => xAxisScale.value(idx))
                .y((d) => y(d))
                .curve(d3.curveBasis)
        );

    bindTooltipHandlers();
});

/**
 * Add mouse events for the chart tooltip
 */
const bindTooltipHandlers = () => {
    svg.value.on("mousemove", tooltipMouseMove);
    svg.value.on("mouseout", tooltipMouseOut);
};

/**
 * When the mouse moves over the svg, get the value the user is hovering over and display it in a tooltip
 * @param {*} event the mouse event containing the text to display and position to display it at
 */
const tooltipMouseMove = (event) => {
    const [gX, gY] = d3.pointer(event, svg.value.node());
    if (gX < margin.left || gX > width.value + margin.right) return;
    if (gY > height.value + margin.top) return;
    const date = xAxisScale.value.invert(gX);
    tooltipData.value = {
        date: Math.floor(date - 1),
        value: props.chartData[Math.floor(date - 1)],
    };
    tooltipPosition.value = [event.pageX - 50, event.pageY];
};

/**
 * When the mouse leaves the svg, set the text to blank. This hides the tooltip
 */
const tooltipMouseOut = () => {
    tooltipData.value = null;
};
</script>

<style lang="scss">
.hydrologic-line-tooltip {
    text-align: start;
}
</style>
