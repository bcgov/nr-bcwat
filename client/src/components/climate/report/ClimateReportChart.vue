<template>
    <div class="chart-area">
        <div class="chart-controls">
            <q-select
                :model-value="yearlyData"
                class="yearly-input"
                :options="yearlyDataOptions"
                label="Select"
                hint="Add yearly data"
                clearable
                multiple
                dense
                outline
                @update:model-value="
                    (newval) => {
                        yearlyData = newval ? newval : [];
                        updateChartLegendContents();
                    }
                "
            />
            <q-btn label="Download PNG" icon="mdi-download" outline @click="downloadPng()"/>
        </div>
        <ChartLegend :legend-list="chartLegendArray" />

        <div id="chart-container">
            <div class="svg-wrap">
                <svg class="d3-chart">
                    <!-- d3 chart content renders here -->
                </svg>
            </div>
        </div>
        <p class="q-mb-xl">Data may be from a live sensor and has not gone through QA, so may contain errors.</p>
        <div
            v-if="showTooltip"
            class="chart-tooltip"
            :style="`left: ${tooltipPosition[0]}px; top: ${tooltipPosition[1]}px; `"
        >
            <div v-for="tip in tooltipText" :key="tip.label">
                <div
                    v-if="tip.label === 'Date'"
                    class="tooltip-header text-bold"
                >
                    {{ tip.value }}
                </div>
                <div
                    v-else-if="tip.value || tip.value === 0"
                    class="tooltip-row"
                >
                    <!-- inline handling of the values setting to two decimal places -->
                    <div
                        class="tooltip-box"
                        :style="`background-color: ${tip.bg.slice(0, 7)}`"
                    ></div>
                    <span
                        class="text-bold"
                    >
                        {{ tip.label }}:
                    </span>
                    <span>{{ parseFloat(tip.value).toFixed(2) }}{{ props.chartUnits }}</span>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import * as d3 from "d3";
import sevenDayHistorical from "@/constants/sevenDayHistorical.json";
import { monthAbbrList } from "@/utils/dateHelpers.js";
import { ref, computed, onMounted, watch, onBeforeUnmount } from "vue";
import ChartLegend from "@/components/streamflow/ChartLegend.vue";
import d3ToPng from 'd3-svg-to-png';

const props = defineProps({
    chartData: {
        type: Object,
        default: () => {},
    },
    chartMode: {
        type: String,
        default: '',
    },
    reportName: {
        type: String,
        default: '',
    },
    startYear: {
        type: Number,
        default: 0,
    },
    endYear: {
        type: Number,
        default: 0,
    },
    yAxisLabel: {
        type: String,
        default: '',
    },
    chartUnits: {
        type: String,
        default: '',
    },
});

const colorScale = [
    "#2196F3",
    "#FF9800",
    "#4CAF50",
    "#9C27B0",
    "#795548",
    "#FF80AB",
    "#00897B",
    "#AFB42B",
    "#00BCD4",
];

const chartLegendArray = ref([]);
const yearlyData = ref([]);
const colors = ref(null);

// chart sizing
const margin = {
    top: 10,
    right: 150,
    bottom: 35,
    left: 65,
};
let width = 400;
let height = 200;

// tooltip variables:
const showTooltip = ref(false);
const tooltipText = ref([]);
const tooltipPosition = ref([]);

// to be used as a cache of already-retrieved yearly historical data.
const fetchedYears = ref([]);

// chart-specific variables:
const svgWrap = ref();
const svgEl = ref();
const svg = ref();
const g = ref();
const chartStart = ref();
const chartEnd = ref();
const innerBars = ref();
const outerBars = ref();
const medianLine = ref();
const medianArea = ref();
const hoverLine = ref(null);
const hoverLinePath = ref(null);
const historicalLines = ref(new Map());
const scaleX = ref();
const scaleY = ref();
const gAxisY = ref();
const gGridX = ref();
const gGridY = ref();
let zoom;

watch(() => yearlyData.value, (newVal, oldVal) => {
    // fetch data for the newly added year only
    const diff = newVal.filter((x) => !oldVal.includes(x));
    // TODO make API POST call for the data for the newly added year
    if (diff.length > 0) {
        historicalLines.value[diff[0]] = formatLineData(sevenDayHistorical);
    }
    updateChart();
});

/**
 * determine which years of data are available for the point
 */
const yearlyDataOptions = computed(() => {
    const myYears = [];
    for (let d = props.startYear; d <= props.endYear; d += 1) {
        myYears.push(d)
    }
    return myYears;
});

watch(() => chartLegendArray.value, () => {
    updateChart();
});

onMounted(() => {
    window.addEventListener("resize", updateChart);
    updateChartLegendContents();
    updateChart();
});

onBeforeUnmount(() => {
    svg.value.selectAll("*").remove();
});

/**
 * handler for fetching a color from the pre-defined color scale and
 * creating a list of legend items
 */
const updateChartLegendContents = () => {
    chartLegendArray.value = [];
    colors.value = colors.value || d3.scaleOrdinal(colorScale);
    yearlyData.value.forEach((year, idx) => {
        chartLegendArray.value.push({
            label: year,
            color: colors.value(idx),
        });
    });
    if (props.chartMode === 'precipitation') {
        chartLegendArray.value.push({
            label: "Current MTD",
            color: "#b3d4fc",
        });
    } else if (props.chartMode === 'temperature') {
        chartLegendArray.value.push({
            label: "Current Max",
            color: "#b3d4fc",
        });
        chartLegendArray.value.push({
            label: "Current Min",
            color: "#b3d4fc",
        });
    } else if (props.chartMode === 'snow-on-ground') {
        chartLegendArray.value.push({
            label: "Current Snow Depth",
            color: "#b3d4fc",
        });
    } else if (props.chartMode === 'snow-water') {
        chartLegendArray.value.push({
            label: "Current Snow Water Equiv.",
            color: "#b3d4fc",
        });
    }
    if (props.chartMode !== 'temperature') {
        chartLegendArray.value.push({
            label: "Historical Median",
            color: "#888",
        });
    }
    chartLegendArray.value.push({
        label: "Historical 75th %",
        color: "#aab5b5",
    });
    chartLegendArray.value.push({
        label: "Historical 25th %",
        color: "#aab5b5",
    });
    chartLegendArray.value.push({
        label: "Historical 90th %",
        color: "#bbc3c3",
    });
    chartLegendArray.value.push({
        label: "Historical 10th%",
        color: "#bbc3c3",
    });
    chartLegendArray.value.sort((a, b) => a.label - b.label);
};

/**
 * calls the component functions to build the chart and set its data
 */
const init = () => {
    if (svg.value) {
        d3.selectAll(".g-els").remove();
    }

    // set the data from selections to align with the chart range
    setDateRanges();
    svgWrap.value = document.querySelector(".svg-wrap");
    svgEl.value = svgWrap.value.querySelector("svg");
    svg.value = d3
        .select(svgEl.value)
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .attr("transform", `translate(${margin.left}, ${margin.top})`);

    g.value = svg.value
        .append("g")
        .attr("class", "g-els")
        .attr("transform", `translate(${margin.left}, ${margin.top})`);

    if (svgWrap.value) {
        width = svgWrap.value.clientWidth - margin.left - margin.right;
        height = svgWrap.value.clientHeight - margin.top - margin.bottom - 50;
    }

    // build the chart axes
    setAxisX();
    setAxisY();

    // add clip-path element
    const defs = g.value.append("defs");
    defs.append("clipPath")
        .attr("id", "box-clip")
        .append("rect")
        .attr("width", width)
        .attr("height", height);

    addXaxis();
    addYaxis();
    addChartData();
    addHoverEvents();

    defineZoom();
};

/**
 * Sets up zoom event listening and calls the zoomed() function for handling
 */
const defineZoom = () => {
    zoom = d3
        .zoom()
        .scaleExtent([1, 9])
        .extent([
            [0, 0],
            [width, height],
        ])
        .translateExtent([
            [0, 0],
            [width, height],
        ])
        .on("zoom", (event) => {
            zoomed(event);
            event.sourceEvent.preventDefault();
        });

    svg.value
        .append("rect")
        .attr("width", width)
        .attr("height", height)
        .style("fill", "none")
        .style("pointer-events", "all")
        .attr("transform", `translate(0, ${margin.top})`)
        .call(zoom);
};

const zoomed = (event) => {
    tooltipMouseOut();
    const newY = event.transform.rescaleY(scaleY.value);
    const newScaleY = newY.domain(event.transform.rescaleY(newY).domain());

    zoomElements({ newScaleY });
};

const zoomElements = (newScaleObj) => {
    addYaxis(newScaleObj.newScaleY);
    addChartData(newScaleObj.newScaleY);
    addHoverEvents(newScaleObj.newScaleY);
};

/**
 * When the mouse leaves the svg, set the text to blank. This hides the tooltip
 */
const tooltipMouseOut = () => {
    tooltipText.value = [];
    showTooltip.value = false;
    if (hoverLine.value) {
        hoverLine.value.remove();
    }
};

/**
 * When the mouse moves over the svg, get the value the user is hovering over and display it in a tooltip
 * @param {*} event the mouse event containing the text to display and position to display it at
 */
const tooltipMouseMove = (event) => {
    tooltipText.value = [];
    showTooltip.value = true;
    tooltipPosition.value = [event.pageX - 300, event.pageY];
    const [gX, gY] = d3.pointer(event, g.value.node());
    if (gX < 0 || gX > width || gY < 0 || gY > height) {
        tooltipMouseOut();
        return;
    }

    addTooltipText(gX);

    // Add line where the user is hovering
    if (hoverLine.value) {
        hoverLine.value.remove();
    }

    const date = scaleX.value.invert(gX + margin.left - 4);
    hoverLine.value = svg.value.append('g').attr('class', 'hovered')

    hoverLinePath.value = hoverLine.value.append('line')
        .attr('class', 'hovered dashed clipped')
        .attr('x1', scaleX.value(date))
        .attr('y1', margin.top)
        .attr('x2', scaleX.value(date))
        .attr('y2', height + margin.top)
        .attr('stroke', '#444')
        .attr('stroke-width', '2')
};

const addTooltipText = (pos) => {
    const date = scaleX.value.invert(pos);
    const bisect = d3.bisector((d) => new Date(d.d)).center;
    const idx = bisect(props.chartData, date);
    const data = props.chartData[idx];

    tooltipText.value.push({
        label: "Date",
        value: `${monthAbbrList[new Date(data.d).getMonth()]} ${new Date(data.d).getDate()} ${new Date(data.d).getFullYear()}`,
    });
    if (props.chartMode === 'temperature') {
        tooltipText.value.push({
            label: "Current Max",
            value: data.currentMax,
            bg: "#b3d4fc",
        });
        tooltipText.value.push({
            label: "Current Min",
            value: data.currentMin,
            bg: "#b3d4fc",
        });
    } else if (props.chartMode === 'precipitation') {
        tooltipText.value.push({
            label: "Current",
            value: data.currentMax,
            bg: "#b3d4fc",
        });
    } else if (props.chartMode === 'snow-on-ground') {
        tooltipText.value.push({
            label: "Current Snow Depth",
            value: data.currentMax,
            bg: "#b3d4fc",
        });
    } else if (props.chartMode === 'snow-water') {
        tooltipText.value.push({
            label: "Current Snow Water Equiv.",
            value: data.currentMax,
            bg: "#b3d4fc",
        });
    }

    tooltipText.value.push({
        label: "Historical Maximum",
        value: data.max,
        bg: "#bbc3c380",
    });
    tooltipText.value.push({
        label: "Historical 75th Percentile",
        value: data.p75,
        bg: "#aab5b590",
    });
    if (props.chartMode !== 'temperature') {
        tooltipText.value.push({
            label: "Historical Median",
            value: data.p50,
            bg: "#99999980",
        });
    }
    tooltipText.value.push({
        label: "Historical 25th Percentile",
        value: data.p25,
        bg: "#aab5b590",
    });
    tooltipText.value.push({
        label: "Historical Minimum",
        value: data.min,
        bg: "#bbc3c380",
    });

    // if (
    //     chartLegendArray.value.filter((el) => el.label !== "Historical")
    //         .length > 0
    // ) {
    //     return;
    //     chartLegendArray.value
    //         .filter((el) => el.label !== "Historical")
    //         .forEach((year) => {
    //             const yearIdx = bisect(
    //                 fetchedYears.value[`year${year.label}`],
    //                 date
    //             );
    //             const data = fetchedYears.value[`year${year.label}`][yearIdx];
    //             tooltipText.value.push({
    //                 label: year.label,
    //                 value: data.v,
    //                 color: year.color,
    //             });
    //         });
    // }
};

/**
 * Add mouse events for the chart tooltip and hover, if applicable
 */
const addHoverEvents = () => {
    svg.value.on("mousemove", (ev) => tooltipMouseMove(ev));
    svg.value.on("mouseout", tooltipMouseOut);
};

const addOuterBars = (scale = scaleY.value) => {
    if (outerBars.value) d3.selectAll(".bar.outer").remove();
    outerBars.value = g.value
        .selectAll(".bar.outer")
        .data(props.chartData)
        .enter()
        .append("rect")
        .attr("fill", "#bbc3c380")
        .attr("class", "sdf bar outer chart-clipped")
        .attr("x", (d) => scaleX.value(d.d))
        .attr("y", (d) => scale(d.max))
        .attr("width", width / props.chartData.length)
        .attr("height", (d) => Math.abs(scale(d.max) - scale(d.min)));
};

const addInnerbars = (scale = scaleY.value) => {
    if (innerBars.value) d3.selectAll(".bar.inner").remove();
    innerBars.value = g.value
        .selectAll(".bar.inner")
        .data(props.chartData)
        .enter()
        .append("rect")
        .attr("fill", "#aab5b580")
        .attr("class", "sdf bar inner chart-clipped")
        .attr("x", (d) => scaleX.value(d.d))
        .attr("y", (d) => scale(d.p75))
        .attr("width", (d) => width / props.chartData.length)
        .attr("height", (d) => Math.abs(scale(d.p75) - scale(d.p25)));
};

const addMedianLine = (scale = scaleY.value) => {
    if (medianLine.value) d3.selectAll(".line.median").remove();
    medianLine.value = g.value
        .append("path")
        .datum(props.chartData)
        .attr("fill", "none")
        .attr("stroke", "#999999")
        .attr("stroke-width", 2)
        .attr("class", "sdf line median chart-clipped")
        .attr("d", d3
            .line()
            .x((d) => scaleX.value(d.d))
            .y((d) => scale(d.p50))
            .defined((d) => d.p50 !== null && d.p50 !== NaN)
        );
};

const addCurrentArea = (scale = scaleY.value) => {
    if (medianArea.value) d3.selectAll(".area.current").remove();
    medianArea.value = g.value
        .append("path")
        .datum(props.chartData)
        .attr("fill", "#b3d4fc80")
        .attr("stroke", "#b3d4fc")
        .attr("stroke-width", 2)
        .attr("class", "sdf area current chart-clipped")
        .attr("d", d3
            .area()
            .x((d) => scaleX.value(d.d))
            .y0((d) => scale(d.currentMin))
            .y1((d) => scale(d.currentMax))
            .curve(d3.curveBasis)
            .defined((d) => d.currentMax !== null && d.currentMin !== null)
        );
};

const addTodayLine = () => {
    if (medianLine.value) {
        d3.selectAll(".line.today").remove();
        d3.selectAll(".rect.today").remove();
        d3.selectAll(".text.today").remove();
    }
    g.value
        .append("line")
        .attr("class", "sdf line today chart-clipped")
        .attr("x1", scaleX.value(new Date()))
        .attr("y1", 0)
        .attr("x2", scaleX.value(new Date()))
        .attr("y2", height)
        .style("stroke-width", 2)
        .style("stroke", "#000");
    g.value
        .append("rect")
        .attr("class", "sdf rect today chart-clipped")
        .attr("x", scaleX.value(new Date()) - 48)
        .attr("y", -16 + height / 2)
        .style("border-radius", "30px")
        .attr("width", '96px')
        .attr("height", '32px')
        .style("fill", "orange");
    g.value
        .append("text")
        .attr("class", "sdf text today chart-clipped")
        .attr("x", scaleX.value(new Date()))
        .attr("dx", "-43px")
        .attr("y", height / 2)
        .attr("dy", ".35em")
        .text(new Date().toLocaleDateString(undefined, { year: "numeric", month: "short", day: "2-digit"}))
        .style("fill", "white")
        .style("font-weight", "bold");
};

/**
 * appends a path (line) to the chart with a colour that corresponds to the
 * selected year in both the map legend and the chart's tooltip.
 *
 * @param year - the year object containing the year and an associated color
 * @param yearData - the specific historical flow data for the given year
 * @param scale - defaults to the set y scale, otherwise accepts the scale from zooming
 */
const addYearLine = (year, yearData, scale = scaleY.value) => {
    g.value
        .append("path")
        .datum(yearData)
        .attr("fill", "none")
        .attr("stroke", year.color)
        .attr("stroke-width", 2)
        .attr("class", "sdf line median chart-clipped")
        .attr("d", d3
            .line()
            .x((d) => scaleX.value(d.d))
            .y((d) => scale(d.v))
            .defined((d) => d.v !== null && d.v !== 0 && d.v !== NaN)
        );
};

/**
 * chart data consists of a outer/background light grey area, inner darker area, and median line
 * additionally, if the user has selected yearly data, lines are added to the chart for each
 * of the selected years.
 */
const addChartData = async (scale = scaleY.value) => {
    addOuterBars(scale);
    addInnerbars(scale);
    addMedianLine(scale);
    addCurrentArea(scale);
    addTodayLine();

    for (const year of chartLegendArray.value.filter((el) => typeof(el.label) === 'number')) {
        const yearData = await getYearlyData(year);
        addYearLine(year, yearData, scale);
        fetchedYears.value[`year${year.label}`] = yearData;
    }
};

/**
 * Retrieves and formats the yearly data for a given year.
 *
 * @param year - the given year for which we must fetch its associated historical data
 * returns a set of dates and values for the current year to display in the chart.
 */
const getYearlyData = async (year) => {
    // check to see if there is already a set of data for the selected year.
    const foundExistingData = fetchedYears.value.find((el) => el.year === `year${year.label}`);
    if (foundExistingData) {
        return foundExistingData;
    } else {
        // if no data exists for the year, get it.
        // API fetch call to go here.
        const data = sevenDayHistorical.map((el) => {
            return {
                d: new Date(new Date(chartStart.value).getUTCFullYear(), 0, el.d),
                v: parseFloat(el.v * 5), // this scaling is applied for viewing purposes only, given the sample data set.
            };
        });

        return data;
    }
};

const addXaxis = (scale = scaleX.value) => {
    if (gGridX.value) g.value.selectAll(".x").remove();
    gGridX.value = g.value
        .append("g")
        .attr("class", "x axis-grid")
        .call(d3.axisBottom(scale).tickSize(height).ticks(12).tickFormat(""));

    // x axis labels and lower axis line
    g.value
        .append("g")
        .attr("class", "x axis")
        .call(d3.axisBottom(scale).ticks(12).tickFormat(d3.timeFormat("%B")))
        .attr("transform", `translate(0, ${height})`);

    g.value
        .append("text")
        .attr("class", "x axis-label")
        .attr("transform", `translate(${width / 2}, ${height + 35})`)
        .text("Date");
};

const addYaxis = (scale = scaleY.value) => {
    if (gAxisY.value) gAxisY.value.remove();
    if (gGridY.value) g.value.selectAll(".y").remove();
    gAxisY.value = g.value.append("g").call(d3.axisLeft(scale));

    // adds the y-axis grid lines to the chart.
    const yAxisGrid = d3
        .axisLeft(scale)
        .tickSize(-width)
        .tickFormat("")
        .ticks(5);

    if (gGridY.value) gGridY.value.remove();
    gGridY.value = g.value
        .append("g")
        .attr("class", "y axis-grid")
        .call(yAxisGrid);

    g.value
        .append("text")
        .attr("class", "y axis-label")
        .attr("transform", `translate(-50, ${height / 2})rotate(-90)`)
        .text(props.yAxisLabel);
};

/**
 * Sets the d and v keys to their correct values. The mapping may not be necessary in the future
 * as the data response from the API is determined.
 *
 * @param data - the raw data to be formatted
 */
const formatLineData = (data) => {
    try {
        return data.map((el) => {
            return {
                d: el.d,
                v: el.v,
            };
        });
    } catch {
        return [];
    }
};

/**
 * Determines the start and end date of the chart. Data added to the chart will
 * be formatted to fall within this date range.
 */
const setDateRanges = () => {
    chartStart.value = new Date(new Date().setFullYear(new Date().getFullYear() - 1)).setDate(1);
    chartEnd.value = new Date(new Date().setMonth(new Date().getMonth() + 7)).setDate(0);
};

const setAxisX = () => {
    // set x-axis scale
    scaleX.value = d3
        .scaleTime()
        .domain([chartStart.value, chartEnd.value])
        .range([0, width]);
};

const setAxisY = () => {
    let min = props.chartData[0].min;
    let max = props.chartData[0].max;

    props.chartData.forEach(entry => {
        min = Math.min(min, entry.currentMin, entry.min);
        max = Math.max(max, entry.currentMax || 0, entry.max);
    });

    // Y axis
    scaleY.value = d3.scaleLinear().range([height, 0]).domain([min * 1.1, max * 1.1]);
};

/**
 * Ensures the chart dimensions and content are resized when the windows is adjusted
 */
const updateChart = () => {
    // timeout catches some potential rendering issues.
    setTimeout(() => {
        init();
    }, 100);
};

const downloadPng = () => {
    d3ToPng('.svg-wrap', `${props.reportName}-${props.chartMode}`);
};
</script>

<style lang="scss">
.chart-area {
    display: flex;
    flex-direction: column;
    height: 100vh;

    .chart-controls {
        display: flex;
        align-items: center;
        justify-content: space-between;

        .yearly-input {
            width: 30%;
        }
    }
    .chart-tooltip {
        position: absolute;
        background-color: rgba(0, 0, 0, 0.6);
        // background-color: white;
        border: 1px solid $light-grey-accent;
        border-radius: 3px;
        color: white;
        display: flex;
        flex-direction: column;
        pointer-events: none;

        .tooltip-header {
            font-size: 18px;
            padding: 0.25em 0.8em;
        }

        .tooltip-row {
            align-items: center;
            display: flex;
            padding: 0.25em 1em;

            .tooltip-box {
                margin-right: 0.25em;
                width: 15px;
                height: 15px;
                border: 1px solid white;
                border-radius: 3px;
            }
        }
    }

    #chart-container {
        height: 100%;
    }

    .svg-wrap {
        background-color: white;
        width: 100%;
        height: 100%;

        .d3-chart {
            width: 100%;
            height: 100%;
        }
    }

    .dashed {
        stroke-dasharray: 5, 6;
    }

    .x.axis {
        path {
            stroke: black;
        }
    }
    .x.axis-grid {
        line {
            stroke: rgba(201, 201, 201, 0.9);
        }
        .domain {
            stroke-opacity: 0;
        }
    }

    .y.axis-grid {
        pointer-events: none;

        line {
            stroke: rgba(201, 201, 201, 0.9);
        }
        .domain {
            stroke-opacity: 0;
        }
    }

    // elements clipped by the clip-path rectangle
    .chart-clipped {
        clip-path: url("#box-clip");
    }
}

</style>
