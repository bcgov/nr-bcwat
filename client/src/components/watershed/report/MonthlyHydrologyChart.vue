<template>
    <div>
        <div :id="`${props.chartId}`"></div>
        <div
            v-if="tooltipData"
            class="watershed-report-tooltip"
            :style="`top: ${tooltipPosition[1]}px; left: ${tooltipPosition[0]}px;`"
        >
            <h3 class="q-ma-none">{{ tooltipData.group }}</h3>
            <table>
                <tbody>
                    <tr>
                        <td>Existing Allocations:</td>
                        <td>{{ (+tooltipData.existing).toFixed(2) }} m³/s</td>
                    </tr>
                    <tr>
                        <td>Risk Management 3:</td>
                        <td>≥ {{ tooltipData.rm3 }} m³/s</td>
                    </tr>
                    <tr>
                        <td>Risk Management 2:</td>
                        <td>{{ tooltipData.rm2 }} m³/s</td>
                    </tr>
                    <tr>
                        <td>Risk Management 1:</td>
                        <td>{{ tooltipData.rm1 }} m³/s</td>
                    </tr>
                    <tr>
                        <td>MAD:</td>
                        <td>{{ props.mad.toFixed(2) }} m³/s</td>
                    </tr>
                    <tr>
                        <td>MAD 20%:</td>
                        <td>{{ (props.mad * 0.2).toFixed(2) }} m³/s</td>
                    </tr>
                    <tr>
                        <td>MAD 10%:</td>
                        <td>{{ (props.mad * 0.1).toFixed(2) }} m³/s</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>

<script setup>
import { monthAbbrList } from "@/utils/dateHelpers";
import * as d3 from "d3";
import { computed, onMounted, ref } from "vue";

const props = defineProps({
    chartData: {
        type: Object,
        default: () => {},
    },
    chartId: {
        type: String,
        default: "",
    },
    mad: {
        type: Number,
        default: 0,
    },
});

const svg = ref(null);
const tooltipPosition = ref([0, 0]);
const tooltipData = ref();

const maxY = computed(() => {
    let maxValue = 0;
    monthAbbrList.forEach((_, idx) => {
        maxValue = Math.max(
            maxValue,
            +props.chartData.existingAllocations[idx],
            +props.chartData.rm1[idx],
            +props.chartData.rm2[idx],
            +props.chartData.rm3[idx].replace("≥ ", ""),
            +props.chartData.monthlyDischarge[idx],
            props.chartData.meanAnnualDischarge
        );
    });
    return maxValue * 1.1;
});

onMounted(() => {
    const myElement = document.getElementById(props.chartId);
    const margin = { top: 10, right: 30, bottom: 20, left: 50 };
    const width = myElement?.offsetWidth + 600 - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    // append the svg object to the body of the page
    svg.value = d3
        .select(`#${props.chartId}`)
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    const myData = [];

    monthAbbrList.forEach((__, idx) => {
        myData.push({
            group: monthAbbrList[idx],
            existing: props.chartData.existingAllocations[idx],
            rm1: props.chartData.rm1[idx],
            rm2: props.chartData.rm2[idx],
            rm3: props.chartData.rm3[idx].replace("≥ ", ""),
        });
    });
    const subgroups = ["existing", "rm1", "rm2", "rm3"];

    // Add X axis
    const x = d3
        .scaleBand()
        .domain(monthAbbrList)
        .range([0, width])
        .padding([0.2]);
    svg.value
        .append("g")
        .attr("transform", `translate(0, ${height})`)
        .call(d3.axisBottom(x).tickSizeOuter(0));

    // Add Y axis
    const y = d3.scaleLinear().domain([0, maxY.value]).range([height, 0]);
    svg.value.append("g").call(d3.axisLeft(y));

    // Set colours for data
    const color = d3
        .scaleOrdinal()
        .domain(subgroups)
        .range(["#c00", "#194666", "#3082be", "#99c6e6"]);

    // Create stacked data
    const stackedData = d3.stack().keys(subgroups)(myData);

    // Show the bars
    svg.value
        .append("g")
        .selectAll("g")
        .data(stackedData)
        .join("g")
        .attr("fill", (d) => color(d.key))
        .attr("stroke", "black")
        .selectAll("rect")
        .data((d) => d)
        .join("rect")
        .attr("x", (d) => x(d.data.group))
        .attr("y", (d) => y(d[1]))
        .attr("height", (d) => y(d[0]) - y(d[1]))
        .attr("width", x.bandwidth());

    // Add mean annual discharge lines
    const mad = props.chartData.meanAnnualDischarge;
    svg.value
        .append("path")
        .attr(
            "d",
            d3.line()([
                [0, y(mad)],
                [width, y(mad)],
            ])
        )
        .attr("stroke", "#ff5722")
        .attr("stroke-width", 2)
        .attr("fill", "none")
        .style("stroke-dasharray", "3, 3");

    svg.value
        .append("path")
        .attr(
            "d",
            d3.line()([
                [0, y(mad * 0.2)],
                [width, y(mad * 0.2)],
            ])
        )
        .attr("stroke", "#ff9800")
        .attr("stroke-width", 2)
        .attr("fill", "none")
        .style("stroke-dasharray", "3, 3");

    svg.value
        .append("path")
        .attr(
            "d",
            d3.line()([
                [0, y(mad * 0.1)],
                [width, y(mad * 0.1)],
            ])
        )
        .attr("stroke", "#ffc107")
        .attr("stroke-width", 2)
        .attr("fill", "none")
        .style("stroke-dasharray", "3, 3");

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
    tooltipData.value = event.srcElement.__data__?.data;
    tooltipPosition.value = [event.pageX - 50, event.pageY - 200];
};

/**
 * When the mouse leaves the svg, set the text to blank. This hides the tooltip
 */
const tooltipMouseOut = () => {
    tooltipData.value = null;
};
</script>

<style lang="scss" scoped>
.watershed-report-tooltip {
    flex-direction: column;

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
