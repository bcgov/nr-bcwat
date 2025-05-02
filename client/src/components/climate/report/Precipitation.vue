<template>
    <div class="precipitation-container">
        <div class="spaced-flex-row">
            AHHHH
            <q-btn icon="mdi-download" label="Download PNG" outline />
        </div>
        <div id="precipitation-chart" />
        {{ maxY }}
        <pre>{{ Object.keys(props.reportContent) }}</pre>
        <pre>{{ props.reportContent.precipitation.historical }}</pre>
    </div>
</template>

<script setup>
import { monthAbbrList } from "@/utils/dateHelpers";
import * as d3 from "d3";
import { computed, onMounted, ref } from "vue";

const props = defineProps({
    reportContent: {
        type: Object,
        default: () => {},
    },
});

const svg = ref(null);
const xScale = ref();
const gGridX = ref();
const margin = { top: 10, right: 30, bottom: 20, left: 50 };
const width = ref();

const maxY = computed(() => {
    let maxValue = 0;
    maxValue = Math.max(
        0,
        ...props.reportContent.precipitation.current.map(
            (entry) => entry.v || 0
        )
    );
    maxValue = Math.max(
        0,
        ...props.reportContent.precipitation.historical.map(
            (entry) => entry.p90 || 0
        )
    );
    return maxValue * 1.1;
});

onMounted(() => {
    const myElement = document.getElementById("precipitation-chart");
    width.value = myElement.offsetWidth - margin.left - margin.right;
    const height = myElement.offsetHeight - margin.top - margin.bottom;
    console.log(width.value, height);

    // append the svg object to the body of the page
    svg.value = d3
        .select(`#precipitation-chart`)
        .append("svg")
        .attr("width", width.value + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    const myData = [];
    const midData = [];
    // monthAbbrList.forEach((__, idx) => {
    //     myData.push({
    //         group: monthAbbrList[idx],
    //         candidate1: props.chartData["Candidate 1"]["90th"][idx + 1],
    //         candidate2: props.chartData["Candidate 2"]["90th"][idx + 1],
    //         candidate3: props.chartData["Candidate 3"]["90th"][idx + 1],
    //         candidate1min: props.chartData["Candidate 1"]["10th"][idx + 1],
    //         candidate2min: props.chartData["Candidate 2"]["10th"][idx + 1],
    //         candidate3min: props.chartData["Candidate 3"]["10th"][idx + 1],
    //     });
    //     midData.push({
    //         group: monthAbbrList[idx],
    //         candidate1: props.chartData["Candidate 1"]["75th"][idx + 1],
    //         candidate2: props.chartData["Candidate 2"]["75th"][idx + 1],
    //         candidate3: props.chartData["Candidate 3"]["75th"][idx + 1],
    //         candidate1min: props.chartData["Candidate 1"]["25th"][idx + 1],
    //         candidate2min: props.chartData["Candidate 2"]["25th"][idx + 1],
    //         candidate3min: props.chartData["Candidate 3"]["25th"][idx + 1],
    //     });
    // });

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
    return;

    // Add Y axis
    const y = d3.scaleLinear().domain([0, maxY.value]).range([height, 0]);
    svg.value.append("g").call(d3.axisLeft(y));

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
                return { key: key, value: d[key], min: d[`${key}min`] };
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
                return { key: key, value: d[key], min: d[`${key}min`] };
            });
        })
        .join("rect")
        .attr("x", (d) => xSubgroup(d.key))
        .attr("y", (d) => y(d.value))
        .attr("width", xSubgroup.bandwidth())
        .attr("height", (d) => height - y(d.value - d.min))
        .attr("fill", (d) => midColor(d.key));

    // // Add mean annual discharge lines
    // addMadLine(width.value, y(props.mad), "#ff5722");
    // addMadLine(width.value, y(props.mad * 0.2), "#ff9800");
    // addMadLine(width.value, y(props.mad * 0.1), "#ffc107");

    // // Add mean line
    // monthAbbrList.forEach((__, idx) => {
    //     addMeanLine(y(props.mean[idx]), idx);
    // });
});

// const addMadLine = (width, value, color) => {
//     svg.value
//         .append("line")
//         .attr("x1", 0)
//         .attr("y1", value)
//         .attr("x2", width)
//         .attr("y2", value)
//         .attr("stroke", color)
//         .attr("stroke-width", 2)
//         .attr("fill", "none")
//         .style("stroke-dasharray", "10, 3");
// };

// const addMeanLine = (value, start) => {
//     let endPos;
//     if (!monthAbbrList[start + 1]) {
//         endPos = width.value;
//     } else {
//         endPos = xScale.value(monthAbbrList[start + 1]);
//     }

//     svg.value
//         .append("line")
//         .attr("x1", xScale.value(monthAbbrList[start]))
//         .attr("y1", value)
//         .attr("x2", endPos)
//         .attr("y2", value)
//         .attr("stroke", "#000")
//         .attr("stroke-width", 2)
//         .attr("fill", "none")
//         .style("stroke", "10, 3");
// };
</script>

<style lang="scss">
#precipitation-chart {
    min-height: 30vh;
    border: 1px solid aqua;
}
</style>
