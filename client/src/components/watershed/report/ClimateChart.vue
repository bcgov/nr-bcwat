<template>
    <div>
        <div :id="props.chartId"></div>
        <div class="climate-legend">
            <div>
                <p>Normal / Historical Average</p>
                <div class="climate-line"></div>
            </div>
            <div>
                <p>Projected Average for 2050s</p>
                <div class="climate-box"></div>
            </div>
        </div>
        <div
            v-if="tooltipData"
            class="climate-tooltip"
            :style="`top: ${tooltipPosition[1]}px; left: ${tooltipPosition[0]}px;`"
        >
            {{ tooltipData }}
        </div>
    </div>
</template>

<script setup>
import { monthAbbrList } from "@/constants/dateHelpers";
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
    areaColor: {
        type: String,
        default: "",
    },
    lineColor: {
        type: String,
        default: "",
    },
});

const svg = ref(null);
const tooltipData = ref(null);
const tooltipPosition = ref([0, 0]);

const formattedChartData = computed(() => {
    const myData = [];

    monthAbbrList.forEach((__, idx) => {
        myData.push({
            group: monthAbbrList[idx],
            normal: props.chartData.historical[idx],
            min: props.chartData.future[idx].min,
            max: props.chartData.future[idx].max,
        });
    });

    return myData;
});

const minY = computed(() => {
    let minValue = 999;
    formattedChartData.value.forEach((month) => {
        minValue = Math.min(minValue, month.min, month.normal);
    });
    return minValue;
});
const maxY = computed(() => {
    let maxValue = -999;
    formattedChartData.value.forEach((month) => {
        maxValue = Math.max(maxValue, month.max, month.normal);
    });
    return maxValue;
});

onMounted(async () => {
    const myElement = document.getElementById(props.chartId);
    const margin = { top: 20, right: 30, bottom: 30, left: 60 };
    const width = myElement.offsetWidth - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    // append the svg object to the body of the page
    svg.value = d3
        .select(`#${props.chartId}`)
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    // List of groups = species here = value of the first column called group -> I show them on the X axis
    const groups = formattedChartData.value.map((d) => d.group);

    // Add X axis
    const x = d3.scaleBand().domain(groups).range([0, width]).padding([0.2]);
    svg.value
        .append("g")
        .attr("transform", `translate(0, ${height})`)
        .call(d3.axisBottom(x).tickSizeOuter(0));

    // Add Y axis
    const y = d3
        .scaleLinear()
        .domain([minY.value, maxY.value])
        .range([height, 0]);
    svg.value.append("g").call(d3.axisLeft(y));

    // Plot the area
    svg.value
        .append("path")
        .datum(formattedChartData.value)
        .attr("fill", props.areaColor)
        .attr(
            "d",
            d3
                .area()
                .x((d) => x(d.group))
                .y0((d) => y(d.min))
                .y1((d) => y(d.max))
                .curve(d3.curveBasis)
        );

    svg.value
        .append("path")
        .datum(formattedChartData.value)
        .attr("fill", "none")
        .attr("stroke", props.lineColor)
        .attr("stroke-width", 1.5)
        .attr(
            "d",
            d3
                .line()
                .x((d) => x(d.group))
                .y((d) => y(d.normal))
                .curve(d3.curveBasis)
        );

    bindTooltipHandlers();
});

/**
 * Add mouse events for the chart tooltip
 */
const bindTooltipHandlers = () => {
    svg.value.on("mousemove", (ev) => tooltipMouseMove(ev));
    svg.value.on("mouseout", tooltipMouseOut);
};

/**
 * When the mouse moves over the svg, get the value the user is hovering over and display it in a tooltip
 * @param {*} event the mouse event containing the text to display and position to display it at
 */
const tooltipMouseMove = (event) => {
    tooltipData.value = event.srcElement.__data__;
    tooltipPosition.value = [event.pageX - 50, event.pageY - 200];
};

/**
 * When the mouse leaves the svg, set the text to blank. This hides the tooltip
 */
const tooltipMouseOut = () => {
    tooltipData.value = null;
};
</script>

<style lang="scss">
.climate-tooltip {
    background-color: rgba(255, 255, 255, 0.95);
    border: 1px solid $light-grey-accent;
    border-radius: 3px;
    display: flex;
    flex-direction: column;
    padding: 1em;
    position: absolute;
    pointer-events: none;

    td {
        text-align: start;
        &:first-child {
            text-align: end;
        }
        &:last-child {
            font-weight: bold;
        }
    }
}
</style>
