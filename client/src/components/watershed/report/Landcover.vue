<template>
    <div class="q-my-lg">
        <h1 class="q-my-lg">Landcover</h1>
        <p>
            The landcover<NoteLink :note-number="16" /> characteristics
            influence hydrologic processes in a watershed<NoteLink
                :note-number="17"
            />. The chart below shows the landcover makeup of the Halden Creek
            watershed. These components were incorporated in the hydrologic
            model that produces the water supply estimates in this report,
            primarily influencing the evapotranspiration component of the water
            budget calculations, which represent the amount of water that moves
            directly back to the atmosphere through direct evaporation or
            transpiration by vegetation.
        </p>
        <div class="landcover-container">
            <div id="landcover-pie-chart"></div>
            <q-table
                :rows="rows"
                :columns="columns"
                row-key="name"
                flat
                :hide-pagination="true"
                :pagination="pagination"
            >
                <template #body="props">
                    <q-tr :props="props">
                        <q-td class="icon-column">
                            <div
                                class="icon"
                                :class="props.row.type.toLowerCase()"
                            />
                        </q-td>
                        <q-td>
                            {{ props.row.type }}
                        </q-td>
                        <q-td :style="{ 'text-align': 'right' }">
                            {{ parseFloat(props.row.area).toFixed(1) }}
                        </q-td>
                        <q-td :style="{ 'text-align': 'right' }">
                            {{ parseFloat(props.row.percentage).toFixed(1) }}%
                        </q-td>
                    </q-tr>
                </template>
            </q-table>
        </div>
        <div
            v-if="tooltipText"
            class="watershed-report-tooltip"
            :style="`top: ${tooltipPosition[1]}px; left: ${tooltipPosition[0]}px;`"
        >
            {{ tooltipText }}
        </div>
        <hr class="q-my-xl" />
    </div>
</template>

<script setup>
import NoteLink from "@/components/watershed/report/NoteLink.vue";
import * as d3 from "d3";
import { computed, onMounted, ref } from "vue";

const props = defineProps({
    reportContent: {
        type: Object,
        default: () => {},
    },
});

const pagination = { rowsPerPage: 0 };

const categoryList = [
    {
        name: "Barren",
        key: "barren",
        color: "#540000",
    },
    {
        name: "Coniferous",
        key: "coniferous",
        color: "#005400",
    },
    {
        name: "Cropland",
        key: "cropland",
        color: "#eca231",
    },
    {
        name: "Deciduous",
        key: "deciduous",
        color: "#54aa00",
    },
    {
        name: "Developed",
        key: "developed",
        color: "#f00",
    },
    {
        name: "Grassland",
        key: "grassland",
        color: "#ffff7e",
    },
    {
        name: "Herb",
        key: "herb",
        color: "#0a0",
    },
    {
        name: "Mixed",
        key: "mixed",
        color: "#545400",
    },
    {
        name: "Shrub",
        key: "shrub",
        color: "#af0",
    },
    {
        name: "Snow / Glacier",
        key: "snow",
        color: "#cfcfcf",
    },
    {
        name: "Water",
        key: "water",
        color: "#388edb",
    },
    {
        name: "Wetland",
        key: "wetland",
        color: "#aa0",
    },
];

const columns = [
    {
        name: "color",
        label: "",
    },
    {
        name: "type",
        field: "type",
        label: "Type",
        align: "left",
        sortable: true,
    },
    {
        name: "area",
        field: "area",
        label: "Area (km²)",
        align: "right",
        sortable: true,
    },
    {
        name: "percentage",
        field: "percentage",
        label: "% of Watershed",
        align: "right",
        sortable: true,
    },
];

const rows = computed(() => {
    const myRows = [];
    categoryList.forEach((category) => {
        myRows.push({
            type: category.name,
            color: category.color,
            area: props.reportContent.overview[category.key],
            percentage: props.reportContent.overview[category.key],
        });
    });
    return myRows;
});

const svg = ref(null);
const tooltipText = ref("");
const tooltipPosition = ref([0, 0]);

// TODO May need this when we get real data
// const totalArea = computed(() => {
//     let total = 0;
//     categoryList.forEach((category) => {
//         total += props.reportContent.overview[category.key];
//     });
//     return total;
// });

onMounted(() => {
    const width = 450;
    const height = 450;
    const margin = 40;
    const radius = Math.min(width, height) / 2 - margin;

    // append the svg object to the div called 'landcover-pie-chart'
    svg.value = d3
        .select("#landcover-pie-chart")
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

    const data = {};
    const colorList = [];
    categoryList.forEach((category) => {
        data[category.name] = props.reportContent.overview[category.key];
        colorList.push(category.color);
    });

    // set the color scale
    const color = d3.scaleOrdinal().range(colorList);

    // Compute the position of each group on the pie:
    const pie = d3.pie().value(function (d) {
        return d[1];
    });
    const data_ready = pie(Object.entries(data));

    // Build the pie chart: Basically, each part of the pie is a path that we build using the arc function.
    svg.value
        .selectAll("whatever")
        .data(data_ready)
        .join("path")
        .attr("d", d3.arc().innerRadius(0).outerRadius(radius))
        .attr("fill", function (d) {
            return color(
                categoryList.find((cat) => cat.name === d.data[0]).color
            );
        });
    // .attr("stroke", "black") // adds an outline
    // .style("stroke-width", "2px");
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
    tooltipText.value = `${
        event.srcElement.__data__.data[0]
    }: ${event.srcElement.__data__.data[1].toFixed(1)}%`;
    tooltipPosition.value = [event.pageX - 50, event.pageY];
};

/**
 * When the mouse leaves the svg, set the text to blank. This hides the tooltip
 */
const tooltipMouseOut = () => {
    tooltipText.value = "";
};
</script>

<style lang="scss">
.landcover-container {
    display: grid;
    grid-template-columns: 50% 50%;
    align-items: center;

    table {
        color: $primary-font-color;
    }

    th {
        font-weight: bold;
    }

    .icon {
        width: 12px;
        height: 12px;
        border: 1px solid black;
        border-radius: 2px;

        &.barren {
            background-color: $color-watershed-landcover-barren;
        }
        &.coniferous {
            background-color: $color-watershed-landcover-coniferous;
        }
        &.cropland {
            background-color: $color-watershed-landcover-cropland;
        }
        &.deciduous {
            background-color: $color-watershed-landcover-deciduous;
        }
        &.developed {
            background-color: $color-watershed-landcover-developed;
        }
        &.grassland {
            background-color: $color-watershed-landcover-grassland;
        }
        &.herb {
            background-color: $color-watershed-landcover-herb;
        }
        &.mixed {
            background-color: $color-watershed-landcover-mixed;
        }
        &.shrub {
            background-color: $color-watershed-landcover-shrub;
        }
        &.snow {
            background-color: $color-watershed-landcover-snow-glacier;
        }
        &.water {
            background-color: $color-watershed-landcover-water;
        }
        &.wetland {
            background-color: $color-watershed-landcover-wetland;
        }
    }
}
.watershed-report-tooltip {
    font-weight: bold;
}
</style>
