<template>
    <div class="hydrologic-bar-chart-container q-my-xl">
        <div class="legend-container">
            <table class="candidate-table">
                <tbody>
                    <tr>
                        <td class="flex">
                            <span
                                class="legend-circle"
                                :style="{'background-color': '#8f3d96'}"
                            />
                        </td>
                        <td><p>Candidate 1</p></td>
                    </tr>
                    <tr>
                        <td class="flex">
                            <span
                                class="legend-circle"
                                :style="{'background-color': '#32429b'}"
                            />
                        </td>
                        <td><p>Candidate 2</p></td>
                    </tr>
                    <tr>
                        <td class="flex">
                            <span
                                class="legend-circle"
                                :style="{'background-color': '#418ecc'}"
                            />
                        </td>
                        <td>Candidate 3</td>
                    </tr>
                </tbody>
            </table>

            <div class="mfp-container">
                <span>Monthly flow percentile</span>
            </div>

            <table class="mad-table">
                <tbody>
                    <tr>
                        <td>Mean</td>
                        <td>Varies</td>
                        <td>
                            <div
                                class="legend-line"
                            >
                                <div
                                    class="visual line"
                                />
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <td>MAD</td>
                        <td>{{ props.mad.toFixed(2) }}m³/s</td>
                        <td>
                            <div
                                class="legend-line"
                            >
                                <div
                                    class="visual line dashed mad"
                                />
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <td>MAD 20%</td>
                        <td>{{ (props.mad * 0.2).toFixed(2) }}m³/s</td>
                        <td>
                            <div
                                class="legend-line"
                            >
                                <div
                                    class="visual line dashed mad20"
                                />
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <td>MAD 10%</td>
                        <td>{{ (props.mad * 0.1).toFixed(2) }}m³/s</td>
                        <td>
                            <div
                                class="legend-line"
                            >
                                <div
                                    class="visual line dashed mad10"
                                />
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
            <!-- <pre>{{ props.chartData }}</pre> -->
            <!-- {{ props.mad }} -->
        </div>
        <div id="hydrologic-bar-chart"></div>
    </div>
    <!-- <pre>{{ props.chartData }}</pre> -->
</template>

<script setup>
import { monthAbbrList } from "@/constants/dateHelpers";
import * as d3 from "d3";
import { computed, onMounted, ref } from "vue";

const props = defineProps({
    chartData: {
        type: Object,
        default: () => {},
    },
    mad: {
        type: Number,
        default: 0,
    },
});

const svg = ref(null);

const maxY = computed(() => {
    let maxValue = 0;
    Object.keys(props.chartData).forEach(key => {
        monthAbbrList.forEach((_, idx) => {
            maxValue = Math.max(
                maxValue,
                props.chartData[key]['90th'][idx] || 0
            );
        });
    });
    return maxValue * 1.1;
});

onMounted(() => {
    const myElement = document.getElementById("hydrologic-bar-chart");
    const margin = { top: 10, right: 30, bottom: 20, left: 50 };
    const width = myElement.offsetWidth - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    // append the svg object to the body of the page
    svg.value = d3
        .select(`#hydrologic-bar-chart`)
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    const myData = [];
    monthAbbrList.forEach((__, idx) => {
        myData.push({
            group: monthAbbrList[idx],
            candidate1: props.chartData['Candidate 1']['90th'][idx+1],
            candidate2: props.chartData['Candidate 2']['90th'][idx+1],
            candidate3: props.chartData['Candidate 3']['90th'][idx+1],
        });
    });
     
    const subgroups = ["candidate1", "candidate2", "candidate3"];

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
        .range(["#8f3d96", "#32429b", "#418ecc"]);

    // Another scale for subgroup position?
    const xSubgroup = d3.scaleBand()
        .domain(subgroups)
        .range([0, x.bandwidth()])
        .padding([0.1])

    // Show the bars
    svg.value.append("g")
        .selectAll("g")
        .data(myData)
        .join("g")
            .attr("transform", d => `translate(${x(d.group)}, 0)`)
        .selectAll("rect")
        .data(function(d) { return subgroups.map(function(key) { return {key: key, value: d[key]}; }); })
        .join("rect")
            .attr("x", d => xSubgroup(d.key))
            .attr("y", d => y(d.value))
            .attr("width", xSubgroup.bandwidth())
            .attr("height", d => height - y(d.value))
            .attr("fill", d => color(d.key));

    // Add mean annual discharge lines
    svg.value
        .append("path")
        .attr(
            "d",
            d3.line()([
                [0, y(props.mad)],
                [width, y(props.mad)],
            ])
        )
        .attr("stroke", "#ff5722")
        .attr("stroke-width", 2)
        .attr("fill", "none")
        .style("stroke-dasharray", "10, 3");

    svg.value
        .append("path")
        .attr(
            "d",
            d3.line()([
                [0, y(props.mad * 0.2)],
                [width, y(props.mad * 0.2)],
            ])
        )
        .attr("stroke", "#ff9800")
        .attr("stroke-width", 2)
        .attr("fill", "none")
        .style("stroke-dasharray", "10, 3");

    svg.value
        .append("path")
        .attr(
            "d",
            d3.line()([
                [0, y(props.mad * 0.1)],
                [width, y(props.mad * 0.1)],
            ])
        )
        .attr("stroke", "#ffc107")
        .attr("stroke-width", 2)
        .attr("fill", "none")
        .style("stroke-dasharray", "10, 3");

});
</script>

<style lang="scss">
.hydrologic-bar-chart-container {
    display: grid;
    grid-template-columns: auto 1fr;
    // min-height: 20rem;

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
        }

        .mfp-container {
            border: 1px solid aqua;
            padding: 1em;
        }

        .mad-table {
            font-size: 0.8em;
            tr {
                td:first-child {
                    text-align: start;
                }
            }
    
            .legend-line {
                display: flex;
                align-items: center;
            
                .line {
                    color: black;
                    border-style: solid;
                    border-width: 2px;
                    width: 2em;
        
                    &.dashed {
                        border-style: dashed;
    
                        &.mad {
                            color: $mad-color;
                        }
                        &.mad20 {
                            color: $mad-20-color;
                        }
                        &.mad10 {
                            color: $mad-10-color;
                        }
                    }
                }
            }
        }
    }
}
</style>
