<template>
    <div>
        <h1 class="q-mb-lg">Topography</h1>
        <p>
            The elevation of a watershed is a primary control on climate,
            vegetation, and timing of hydrologic processes such as onset of
            spring melt. The amount, and state of precipitation changes with
            elevation. Temperatures vary by elevation, with gradients typically
            differing in direction between winter and summer (with valley
            bottoms typically colder in winter than higher elevations, and
            higher alpine areas colder in summer than the valley bottoms). The
            hypsometric curve shown in the chart below, shows the cumulative
            distribution of elevation by area in the watershed. Percent values
            on the x-axis can be used to determine the percentage of the
            watershed above a given elevation value.
        </p>
        <div id="topography-chart"></div>
        <div class="chart-legend">
            <div class="flex">
                <span>Elevation range in watersheds > 300 km², NEBC</span>
                <div
                    class="legend-box"
                    :style="{ 'background-color': '#d3d3d3' }"
                ></div>
            </div>
        </div>
        <div
            v-if="tooltipData"
            class="watershed-report-tooltip"
            :style="`top: ${tooltipPosition[1]}px; left: ${tooltipPosition[0]}px;`"
        >
            {{ tooltipData.x }}% of the watershed is above {{ tooltipData.y }}m
            elevation
        </div>
        <hr />
    </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import * as d3 from "d3";

const props = defineProps({
    reportContent: {
        type: Object,
        default: () => {},
    },
});

const margin = { top: 20, right: 30, bottom: 45, left: 60 };
const width = ref();
const height = ref();
const svg = ref(null);
const g = ref();
const xAxisScale = ref();
const tooltipData = ref(null);
const tooltipPosition = ref([0, 0]);

const formattedChartData = computed(() => {
    return props.reportContent.overview.elevs.map((elev, index) => ({
        x: index,
        y: elev,
        min: props.reportContent.overview.elevs_flat[index],
        max: props.reportContent.overview.elevs_steep[index],
    }));
});

const minY = computed(() => {
    let minValue = 11999;
    formattedChartData.value.forEach((month) => {
        minValue = Math.min(minValue, month.min);
    });
    return minValue;
});
const maxY = computed(() => {
    let maxValue = -11999;
    formattedChartData.value.forEach((month) => {
        maxValue = Math.max(maxValue, month.max);
    });
    return maxValue;
});

onMounted(async () => {
    const myElement = document.getElementById("topography-chart");
    width.value = myElement.offsetWidth - margin.left - margin.right;
    height.value = 300 - margin.top - margin.bottom;

    // append the svg object to the body of the page
    svg.value = d3
        .select("#topography-chart")
        .append("svg")
        .attr("width", width.value + margin.left + margin.right)
        .attr("height", height.value + margin.top + margin.bottom);

    g.value = svg.value
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    // Add X axis
    xAxisScale.value = d3
        .scaleLinear()
        .domain([1, 100])
        .range([1, width.value - margin.right]);
    g.value
        .append("g")
        .attr("transform", `translate(0, ${height.value})`)
        .call(d3.axisBottom(xAxisScale.value));

    // Add X axis label
    g.value
        .append("text")
        .attr("class", "text-capitalize")
        .attr("text-anchor", "end")
        .attr("fill", "#5d5e5d")
        .attr("x", 6)
        .attr("dx", `${width.value / 2}`)
        .attr("dy", height.value + margin.top + 20)

        .text("Cumulative %");

    // Add Y axis
    const y = d3
        .scaleLinear()
        .domain([minY.value, maxY.value])
        .range([height.value, 0]);
    g.value.append("g").call(d3.axisLeft(y));

    // Add Y axis label
    g.value
        .append("text")
        .attr("class", "text-capitalize")
        .attr("text-anchor", "end")
        .attr("fill", "#5d5e5d")
        .attr("y", 6)
        .attr("dx", "-6em")
        .attr("dy", "-4em")
        .attr("transform", "rotate(-90)")
        .text("Elevation (m)");

    // Plot the area
    g.value
        .append("path")
        .datum(formattedChartData.value)
        .attr("fill", "#d3d3d3")
        .attr(
            "d",
            d3
                .area()
                .x((d) => xAxisScale.value(d.x + 1))
                .y0((d) => y(d.min))
                .y1((d) => y(d.max))
                .curve(d3.curveBasis)
        );

    g.value
        .append("path")
        .datum(formattedChartData.value)
        .attr("fill", "none")
        .attr("stroke", "#000")
        .attr("stroke-width", 1.5)
        .attr(
            "d",
            d3
                .line()
                .x((d) => xAxisScale.value(d.x + 1))
                .y((d) => y(d.y))
                .curve(d3.curveBasis)
        );

    g.value
        .append("path")
        .datum(formattedChartData.value)
        .attr("fill", "none")
        .attr("stroke", "#949494")
        .attr("stroke-width", 1.5)
        .attr(
            "d",
            d3
                .line()
                .x((d) => xAxisScale.value(d.x + 1))
                .y((d) => y(d.min))
                .curve(d3.curveBasis)
        );

    g.value
        .append("path")
        .datum(formattedChartData.value)
        .attr("fill", "none")
        .attr("stroke", "#949494")
        .attr("stroke-width", 1.5)
        .attr(
            "d",
            d3
                .line()
                .x((d) => xAxisScale.value(d.x + 1))
                .y((d) => y(d.max))
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
    const date = xAxisScale.value.invert(gX - 60);
    tooltipData.value = formattedChartData.value[Math.floor(date)];
    tooltipPosition.value = [event.pageX - 50, event.pageY];
};

/**
 * When the mouse leaves the svg, set the text to blank. This hides the tooltip
 */
const tooltipMouseOut = () => {
    tooltipData.value = null;
};
</script>
