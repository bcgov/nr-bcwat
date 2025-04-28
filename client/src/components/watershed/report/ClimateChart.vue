<template>
    <div>
        <div :id="`climate-${props.chartId}-chart`"></div>
        <div class="climate-legend">
            <div class="flex">
                <span>Normal / Historical Average</span>
                <div
                    class="climate-line"
                    :style="{ 'background-color': props.lineColor }"
                ></div>
            </div>
            <div class="flex">
                <span>Projected Average for 2050s</span>
                <div
                    class="climate-box"
                    :style="{ 'background-color': props.areaColor }"
                ></div>
            </div>
        </div>
        <div
            v-if="tooltipData"
            class="climate-tooltip"
            :style="`top: ${tooltipPosition[1]}px; left: ${tooltipPosition[0]}px;`"
        >
            <h3 class="q-ma-none">{{ monthAbbrList[tooltipData?.group] }}</h3>
            <table>
                <tbody>
                    <tr>
                        <td>Normal / Historical Average:</td>
                        <td>
                            {{ tooltipData?.normal.toFixed(2) }}
                            {{ chartUnits }}
                        </td>
                    </tr>
                    <tr>
                        <td>Min Projected Average for 2050s:</td>
                        <td>
                            {{ tooltipData?.min.toFixed(2) }}
                            {{ chartUnits }}
                        </td>
                    </tr>
                    <tr>
                        <td>Max Projected Average for 2050s:</td>
                        <td>
                            {{ tooltipData?.max.toFixed(2) }}
                            {{ chartUnits }}
                        </td>
                    </tr>
                </tbody>
            </table>
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

const margin = { top: 20, right: 30, bottom: 30, left: 60 };
const width = ref();
const height = ref();
const svg = ref(null);
const g = ref();
const xAxisScale = ref();
const tooltipData = ref(null);
const tooltipPosition = ref([0, 0]);

const chartUnits = computed(() => {
    return props.chartId === "temperature" ? "°C" : "mm";
});

const formattedChartData = computed(() => {
    const myData = [];

    monthAbbrList.forEach((__, idx) => {
        myData.push({
            group: idx,
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
    const myElement = document.getElementById(`climate-${props.chartId}-chart`);
    width.value = myElement.offsetWidth - margin.left - margin.right;
    height.value = 200 - margin.top - margin.bottom;

    // append the svg object to the body of the page
    svg.value = d3
        .select(`#climate-${props.chartId}-chart`)
        .append("svg")
        .attr("width", width.value + margin.left + margin.right)
        .attr("height", height.value + margin.top + margin.bottom);

    g.value = svg.value
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    // Add X axis
    xAxisScale.value = d3
        .scaleLinear()
        .domain([0, 11])
        .range([0 + 1, width.value - margin.right]);
    g.value
        .append("g")
        .attr("transform", `translate(0, ${height.value})`)
        .call(
            d3
                .axisBottom(xAxisScale.value)
                .tickFormat((_, i) => monthAbbrList[i])
        );

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
        .attr("dx", "-1.5em")
        .attr("dy", "-3em")
        .attr("transform", "rotate(-90)")
        .text(`${props.chartId} (${chartUnits.value})`);

    // Plot the area
    g.value
        .append("path")
        .datum(formattedChartData.value)
        .attr("fill", props.areaColor)
        .attr(
            "d",
            d3
                .area()
                .x((d) => xAxisScale.value(d.group))
                .y0((d) => y(d.min))
                .y1((d) => y(d.max))
                .curve(d3.curveBasis)
        );

    g.value
        .append("path")
        .datum(formattedChartData.value)
        .attr("fill", "none")
        .attr("stroke", props.lineColor)
        .attr("stroke-width", 1.5)
        .attr(
            "d",
            d3
                .line()
                .x((d) => xAxisScale.value(d.group))
                .y((d) => y(d.normal))
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
    const date = xAxisScale.value.invert(gX - 1);
    tooltipData.value = formattedChartData.value[Math.floor(date)];
    tooltipPosition.value = [event.pageX - 50, event.pageY - 150];
};

/**
 * When the mouse leaves the svg, set the text to blank. This hides the tooltip
 */
const tooltipMouseOut = () => {
    tooltipData.value = null;
};
</script>

<style lang="scss">
.climate-legend {
    display: flex;
    justify-content: center;

    .flex {
        align-items: center;
        margin: 1em;
    }

    .climate-line {
        align-items: center;
        height: 0.3em;
        margin-left: 1em;
        width: 3em;
    }

    .climate-box {
        align-items: center;
        border-radius: 3px;
        height: 100%;
        margin-left: 1em;
        width: 3em;
    }
}
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
