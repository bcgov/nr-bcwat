<template>
    <div>
        <h1>Monthly Hydrology</h1>
        <p>
            Hydrologic models have been developed to produce estimates of mean
            monthly flows. The Province of BC’s Environmental Flow Needs Policy
            has been applied to these estimates, identifying risk management
            levels to support water management decisions. Information on active
            water licences and approvals (collectively, ‘allocations’) in the
            watershed have been extracted and summarized from government
            databases and integrated with the hydrology model data and risk
            management level calculations, to account for the volume of water
            already allocated.
        </p>
        <p>
            In the chart below, the height of each column represents the mean
            monthly discharge - the long term, estimated average flow for that
            month of the year. The dark, medium, and light blue areas of the
            columns show the potential amount of water allocations within each
            risk management level. When allocations exist in the watershed, a
            red box hangs down from the top of each column to represent the
            volume of existing allocations in the context of mean monthly
            supply. The table below corresponds to the data shown on the chart.
        </p>
        <hr />
        <!-- <div id="monthly-chart">
            <svg class="svg-webkit-fix" :class="`${props.chartId}`">
            </svg>
        </div> -->
        <div id="my_dataviz"></div>
        <hr />
        <pre>{{ props.reportContent.queryMonthlyHydrology }}</pre>
        <hr />
        <pre>{{ props.reportContent.downstreamMonthlyHydrology }}</pre>
        <hr />
    </div>
</template>

<script setup>
import * as d3 from "d3";
import { computed, onMounted, ref } from "vue";

const svg = ref(null);
const svgWrap = ref();
const g = ref(null);
const width = 400;
const height = 200;
const defs = ref();
const margin = {
    top: 10,
    right: -10,
    bottom: 30,
    left: 40,
};

const scaleX = ref(null);
const scaleY = ref(null);

const props = defineProps({
    reportContent: {
        type: Object,
        default: () => {},
    },
});

onMounted(() => {
    const margin = { top: 10, right: 30, bottom: 20, left: 50 },
        width = 460 - margin.left - margin.right,
        height = 400 - margin.top - margin.bottom;

    // append the svg object to the body of the page
    const svg = d3
        .select("#my_dataviz")
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    const myData = [];

    props.reportContent.queryMonthlyHydrology.existingAllocations.forEach(
        (__, idx) => {
            myData.push({
                group: idx,
                existing:
                    props.reportContent.queryMonthlyHydrology
                        .existingAllocations[idx],
                rm1: props.reportContent.queryMonthlyHydrology.rm1[idx],
                rm2: props.reportContent.queryMonthlyHydrology.rm2[idx],
                rm3: props.reportContent.queryMonthlyHydrology.rm3[idx],
            });
        }
    );
    myData.push(["group", "existing", "rm1", "rm2", "rm3"]);
    const subgroups = ["existing", "rm1", "rm2", "rm3"];

    // List of groups = species here = value of the first column called group -> I show them on the X axis
    const groups = myData.map((d) => d.group);

    // Add X axis
    const x = d3.scaleBand().domain(groups).range([0, width]).padding([0.2]);
    svg.append("g")
        .attr("transform", `translate(0, ${height})`)
        .call(d3.axisBottom(x).tickSizeOuter(0));

    // Add Y axis
    const y = d3.scaleLinear().domain([0, 1]).range([height, 0]);
    svg.append("g").call(d3.axisLeft(y));

    // color palette = one color per subgroup
    const color = d3
        .scaleOrdinal()
        .domain(subgroups)
        .range(["#fff", "#e41a1c", "#377eb8", "#4daf4a"]);

    //stack the myData? --> stack per subgroup
    const stackedData = d3.stack().keys(subgroups)(myData);

    // Show the bars
    svg.append("g")
        .selectAll("g")
        // Enter in the stack data = loop key per key = group per group
        .data(stackedData)
        .join("g")
        .attr("fill", (d) => color(d.key))
        .selectAll("rect")
        // enter a second time = loop subgroup per subgroup to add all rectangles
        .data((d) => d)
        .join("rect")
        .attr("x", (d) => x(d.data.group))
        .attr("y", (d) => y(d[1]))
        .attr("height", (d) => y(d[0]) - y(d[1]))
        .attr("width", x.bandwidth());
});
</script>

<style lang="scss">
#monthly-chart {
    background-color: aqua;
}

.svg-webkit-fix {
    width: 100%;
    height: 100%;
}
</style>
