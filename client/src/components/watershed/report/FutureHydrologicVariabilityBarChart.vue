<template>
    <div class="hydrologic-bar-chart-container q-my-xl">
        <div class="legend-container">
            <table class="candidate-table">
                <tbody>
                    <tr>
                        <td class="flex">
                            <span
                                class="legend-circle"
                                :style="{ 'background-color': '#8f3d96' }"
                            />
                        </td>
                        <td><p>1976-2006</p></td>
                    </tr>
                    <tr>
                        <td class="flex">
                            <span
                                class="legend-circle"
                                :style="{ 'background-color': '#32429b' }"
                            />
                        </td>
                        <td><p>2011-2040</p></td>
                    </tr>
                    <tr>
                        <td class="flex">
                            <span
                                class="legend-circle"
                                :style="{ 'background-color': '#418ecc' }"
                            />
                        </td>
                        <td><p>2041-2070</p></td>
                    </tr>
                    <tr>
                        <td class="flex">
                            <span
                                class="legend-circle"
                                :style="{ 'background-color': '#13bdd5' }"
                            />
                        </td>
                        <td>2071-2100</td>
                    </tr>
                </tbody>
            </table>

            <HydrologicVariabilityLegend />

        </div>
        <div id="hydrologic-bar-chart"></div>
    </div>
</template>

<script setup>
import HydrologicVariabilityLegend from "@/components/watershed/report/HydrologicVariabilityLegend.vue";
import { monthAbbrList } from "@/utils/dateHelpers";
import * as d3 from "d3";
import { computed, onMounted, ref } from "vue";

const props = defineProps({
    chartData: {
        type: Object,
        default: () => {},
    }
});

const svg = ref(null);
const xScale = ref();
const gGridX = ref();
const margin = { top: 10, right: 30, bottom: 20, left: 50 };
const width = ref();

const maxY = computed(() => {
    let maxValue = 0;
    Object.keys(props.chartData).forEach((key) => {
        monthAbbrList.forEach((_, idx) => {
            maxValue = Math.max(
                maxValue,
                props.chartData[key]["90th"][idx] || 0
            );
        });
    });
    return maxValue * 1.1;
});

onMounted(() => {
    const myElement = document.getElementById("hydrologic-bar-chart");
    width.value = myElement.offsetWidth - margin.left - margin.right;
    const height = myElement.offsetHeight - margin.top - margin.bottom;

    // append the svg object to the body of the page
    svg.value = d3
        .select(`#hydrologic-bar-chart`)
        .append("svg")
        .attr("width", width.value + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    const myData = [];
    const midData = [];
    monthAbbrList.forEach((__, idx) => {
        myData.push({
            group: monthAbbrList[idx],
            val1976: props.chartData["1976"]["90th"][idx + 1],
            val2011: props.chartData["2011"]["90th"][idx + 1],
            val2041: props.chartData["2041"]["90th"][idx + 1],
            val2071: props.chartData["2071"]["90th"][idx + 1],
            minval1976: props.chartData["1976"]["10th"][idx + 1],
            minval2011: props.chartData["2011"]["10th"][idx + 1],
            minval2041: props.chartData["2041"]["10th"][idx + 1],
            minval2071: props.chartData["2071"]["10th"][idx + 1],
        });
        midData.push({
            group: monthAbbrList[idx],
            val1976: props.chartData["1976"]["75th"][idx + 1],
            val2011: props.chartData["2011"]["75th"][idx + 1],
            val2041: props.chartData["2041"]["75th"][idx + 1],
            val2071: props.chartData["2071"]["75th"][idx + 1],
            minval1976: props.chartData["1976"]["25th"][idx + 1],
            minval2011: props.chartData["2011"]["25th"][idx + 1],
            minval2041: props.chartData["2041"]["25th"][idx + 1],
            minval2071: props.chartData["2071"]["25th"][idx + 1],
        });
    });

    const subgroups = ["val1976", "val2011", "val2041", "val2071"];

    // Add X axis
    xScale.value = d3.scaleBand().domain(monthAbbrList).range([0, width.value]);

    svg.value
        .append("g")
        .attr("transform", `translate(0, ${height})`)
        .call(d3.axisBottom(xScale.value).tickSizeOuter(0));

    const addXaxis = () => {
        if (gGridX.value) svg.value.selectAll(".x").remove();
        gGridX.value = svg.value
            .append("g")
            .attr("class", "x axis-grid")
            .attr("transform", `translate(${xScale.value.bandwidth() / 2}, 0)`)
            .call(
                d3
                    .axisBottom(xScale.value)
                    .tickSize(height)
                    .ticks(12)
                    .tickFormat("")
            );
    };
    addXaxis();

    // Add Y axis
    const y = d3.scaleLinear().domain([0, maxY.value]).range([height, 0]);
    svg.value.append("g").call(d3.axisLeft(y));

    // Set colours for data
    const color = d3
        .scaleOrdinal()
        .domain(subgroups)
        .range(["#c694c3", "#7a85c1", "#95c8ec", '#89d4e3']);

    const midColor = d3
        .scaleOrdinal()
        .domain(subgroups)
        .range(["#8f3d96", "#32429b", "#418ecc", '#13bdd5',]);

    // Another scale for subgroup position?
    const xSubgroup = d3
        .scaleBand()
        .domain(subgroups)
        .range([0, xScale.value.bandwidth()])
        .padding(0.2)
        .paddingOuter(0.5);

    // Show the bars
    svg.value
        .append("g")
        .selectAll("g")
        .data(myData)
        .join("g")
        .attr("transform", (d) => `translate(${xScale.value(d.group)}, 0)`)
        .selectAll("rect")
        .data(function (d) {
            return subgroups.map(function (key) {
                return { key: key, value: d[key], min: d[`min${key}`] };
            });
        })
        .join("rect")
        .attr("x", (d) => xSubgroup(d.key))
        .attr("y", (d) => y(d.value))
        .attr("width", xSubgroup.bandwidth())
        .attr("height", (d) => height - y(d.value - d.min))
        .attr("fill", (d) => color(d.key));

    // Show the bars
    svg.value
        .append("g")
        .selectAll("g")
        .data(midData)
        .join("g")
        .attr("transform", (d) => `translate(${xScale.value(d.group)}, 0)`)
        .selectAll("rect")
        .data(function (d) {
            return subgroups.map(function (key) {
                return { key: key, value: d[key], min: d[`min${key}`] };
            });
        })
        .join("rect")
        .attr("x", (d) => xSubgroup(d.key))
        .attr("y", (d) => y(d.value))
        .attr("width", xSubgroup.bandwidth())
        .attr("height", (d) => height - y(d.value - d.min))
        .attr("fill", (d) => midColor(d.key));
});

</script>

<style lang="scss">
.x.axis-grid {
    line {
        stroke: rgba(201, 201, 201, 0.9);
    }
    .domain {
        stroke-opacity: 0;
    }
}
.hydrologic-bar-chart-container {
    display: grid;
    grid-template-columns: auto 1fr;

    .legend-container {
        align-items: center;
        display: flex;
        flex-direction: column;
        text-align: center;

        .candidate-table {
            background-color: $dashboard-background-light;
            border-radius: 5px;
            padding: 1em;

            .legend-circle {
                border-radius: 50%;
                height: 20px;
                width: 20px;
            }

            .td {
                margin-bottom: 0em;
                padding-bottom: 0em;
            }
        }
    }
}
</style>
