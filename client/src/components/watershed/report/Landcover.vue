<template>
    <div class="q-my-lg">
        <h1>Landcover</h1>
        <p>
            The landcover characteristics influence hydrologic processes in a
            watershed. The chart below shows the landcover makeup of the Halden
            Creek watershed. These components were incorporated in the
            hydrologic model that produces the water supply estimates in this
            report, primarily influencing the evapotranspiration component of
            the water budget calculations, which represent the amount of water
            that moves directly back to the atmosphere through direct
            evaporation or transpiration by vegetation.
        </p>
        {{ Object.keys(props.reportContent.overview) }}
        <div class="landcover-container">
            <div id="landcover-pie-chart"></div>
            <table>
                <tbody>
                    <tr>
                        <th />
                        <th>Type</th>
                        <th>Area</th>
                        <th>% of Watershed</th>
                    </tr>
                    <tr>
                        <td>BOX</td>
                        <td>Barren</td>
                        <td>
                            {{ props.reportContent.overview.barren }}
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
        <hr />
    </div>
</template>

<script setup>
import * as d3 from "d3";
import { onMounted } from "vue";

const props = defineProps({
    reportContent: {
        type: Object,
        default: () => {},
    },
});

onMounted(() => {
    const width = 450;
    const height = 450;
    const margin = 40;
    const radius = Math.min(width, height) / 2 - margin;

    // append the svg object to the div called 'landcover-pie-chart'
    const svg = d3
        .select("#landcover-pie-chart")
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

    const data = {
        a: props.reportContent.overview.coniferous,
        b: props.reportContent.overview.barren,
        c: props.reportContent.overview.shrub,
        d: props.reportContent.overview.deciduous,
        e: props.reportContent.overview.water,
        f: props.reportContent.overview.mixed,
        g: props.reportContent.overview.herb,
        h: props.reportContent.overview.grassland,
        i: props.reportContent.overview.snow,
        j: props.reportContent.overview.wetland,
        k: props.reportContent.overview.developed,
        l: props.reportContent.overview.cropland,
    };

    console.log(data, props.reportContent.overview);

    // set the color scale
    const color = d3.scaleOrdinal().range([
        "#005400", // coniferous
        "#540000", // barren
        "#af0", // shrub
        "#54aa00", // deciduous
        "#388edb", // water
        "#545400", // mixed
        "#0a0", // herb
        "#ffff7e", // grassland
        "#cfcfcf", // snow
        "#aa0", // wetland
        "#f00", // developed
        "#eca231", // cropland
    ]);

    // Compute the position of each group on the pie:
    const pie = d3.pie().value(function (d) {
        return d[1];
    });
    const data_ready = pie(Object.entries(data));

    // Build the pie chart: Basically, each part of the pie is a path that we build using the arc function.
    svg.selectAll("whatever")
        .data(data_ready)
        .join("path")
        .attr("d", d3.arc().innerRadius(0).outerRadius(radius))
        .attr("fill", function (d) {
            return color(d.data[1]);
        });
    // .attr("stroke", "black") // adds an outline
    // .style("stroke-width", "2px");
    // .style("opacity", 0.7);
});
</script>

<style lang="scss">
.landcover-container {
    display: grid;
    grid-template-columns: 50% 50%;
}
</style>
