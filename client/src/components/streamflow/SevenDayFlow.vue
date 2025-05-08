<template>
    <div class="seven-day-area">
        <div class="seven-day-header">
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
            <div class="chart-legend">
                <ChartLegend :legend-list="chartLegendArray" />
            </div>
        </div>

        <div 
            id="streamflow-chart-container"
        >
            <div class="svg-wrap-sdf">
                <svg class="d3-chart-sdf">
                    <!-- d3 chart content renders here -->
                </svg>
            </div>
        </div>

        <div
            v-if="showTooltip"
            class="seven-day-tooltip"
            :style="`left: ${tooltipPosition[0]}px; top: ${tooltipPosition[1]}px; `"
        >
            <div v-for="tip in tooltipText">
                <div
                    v-if="tip.label === 'Date'"
                    class="tooltip-header text-bold"
                >
                    {{ tip.value }}
                </div>
                <div
                    v-else
                    class="tooltip-row"
                    :style="'bg' in tip ? `background-color: ${tip.bg}` : ''"
                >
                    <!-- inline handling of the values setting to two decimal places -->
                    <span
                        class="text-bold"
                        :style="'color' in tip ? `color: ${tip.color}` : ''"
                    >
                        {{ tip.label }}:
                    </span>
                    <span v-if="tip.value">{{
                        parseFloat(tip.value).toFixed(2)
                    }}</span>
                    <span v-else>No Data</span>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import * as d3 from "d3";
import sevenDay from "@/constants/sevenDay.json";
import sevenDayHistorical from "@/constants/sevenDayHistorical.json";
import { monthAbbrList } from "@/utils/dateHelpers.js";
import { ref, computed, onMounted, watch, onBeforeUnmount } from "vue";
import ChartLegend from "./ChartLegend.vue";

const props = defineProps({
    selectedPoint: {
        type: Object,
        default: () => {},
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
    right: 50,
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
const formattedChartData = ref();
const svgWrap = ref();
const svgEl = ref();
const svg = ref();
const g = ref();
const chartStart = ref();
const chartEnd = ref();
const innerBars = ref();
const outerBars = ref();
const medianLine = ref();
const historicalLines = ref(new Map());
const scaleX = ref();
const scaleY = ref();
const yMax = ref();
const yMin = ref();
const gAxisY = ref();
const gGridX = ref();
const gGridY = ref();
let zoom;

watch(
    () => yearlyData.value,
    (newVal, oldVal) => {
        // fetch data for the newly added year only
        const diff = newVal.filter((x) => !oldVal.includes(x));
        // TODO make API POST call for the data for the newly added year
        if (diff.length > 0) {
            historicalLines.value[diff[0]] = formatLineData(sevenDayHistorical);
        }
        updateChart();
    }
);

/**
 * determine which years of data are available for the point
 */
const yearlyDataOptions = computed(() => {
    if (props.selectedPoint) {
        const arr = [];
        for (
            let i = JSON.parse(props.selectedPoint.yr)[0];
            i <= JSON.parse(props.selectedPoint.yr)[1];
            i++
        ) {
            arr.push(i);
        }
        return arr;
    }
    return [];
});

watch(
    () => chartLegendArray.value,
    () => {
        updateChart();
    }
);

onMounted(() => {
    // TODO find a better way of handling chart update when window resizes. 
    // window.addEventListener("resize", updateChart);
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
    // add the historical label and color
    chartLegendArray.value.push({
        label: "Historical",
        color: "#ddd",
    });
    chartLegendArray.value.sort((a, b) => a.label - b.label);
};

/**
 * calls the component functions to build the chart and set its data
 */
const init = () => {
    if (svg.value) {
        d3.selectAll('.g-els.sdf').remove();
    }

    // set the data from selections to align with the chart range
    setDateRanges();
    formatChartData(sevenDay);
    svgWrap.value = document.querySelector('.svg-wrap-sdf');
    svgEl.value = svgWrap.value.querySelector('svg');
    svg.value = d3.select(svgEl.value)
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        
    g.value = svg.value.append('g')
        .attr('class', 'g-els sdf')
        .attr("transform", `translate(${margin.left}, ${margin.top})`);

    if (svgWrap.value) {
        width = svgWrap.value.clientWidth - margin.left - margin.right;
        height = svgWrap.value.clientHeight - margin.top - margin.bottom;
    }

    // build the chart axes
    setAxisX();
    setAxisY();

    // add clip-path element
    const defs = g.value.append("defs");
    defs.append("clipPath")
        .attr("id", "streamflow-box-clip")
        .append("rect")
        .attr("width", width)
        .attr("height", height);

    addXaxis();
    addYaxis();
    addSevenDayFlowData();
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

    zoomElements({
        newScaleY,
    });
};

const zoomElements = (newScaleObj) => {
    addYaxis(newScaleObj.newScaleY);
    addSevenDayFlowData(newScaleObj.newScaleY);
    addHoverEvents(newScaleObj.newScaleY);
};

/**
 * When the mouse leaves the svg, set the text to blank. This hides the tooltip
 */
const tooltipMouseOut = () => {
    tooltipText.value = [];
    showTooltip.value = false;
};

/**
 * When the mouse moves over the svg, get the value the user is hovering over and display it in a tooltip
 * @param {*} event the mouse event containing the text to display and position to display it at
 */
const tooltipMouseMove = (event) => {
    tooltipText.value = [];
    showTooltip.value = true;
    tooltipPosition.value = [event.pageX - 250, event.pageY];
    const [gX, gY] = d3.pointer(event, g.value.node());
    if (gX < 0 || gX > width || gY < 0 || gY > height) {
        tooltipMouseOut();
        return;
    }

    addTooltipText(gX);
};

const addTooltipText = (pos) => {
    const date = scaleX.value.invert(pos);
    const bisect = d3.bisector((d) => new Date(d.d)).center;
    const idx = bisect(formattedChartData.value, date);
    const data = formattedChartData.value[idx];

    tooltipText.value.push({
        label: "Date",
        value: `${monthAbbrList[new Date(data.d).getMonth()]} ${new Date(
            data.d
        ).getDate()}`,
    });
    tooltipText.value.push({
        label: "Maximum",
        value: data.max,
        bg: "#bbc3c380",
    });
    tooltipText.value.push({
        label: "75th Percentile",
        value: data.p75,
        bg: "#aab5b590",
    });
    tooltipText.value.push({
        label: "Median",
        value: data.p50,
        bg: "#99999980",
    });
    tooltipText.value.push({
        label: "25th Percentile",
        value: data.p25,
        bg: "#aab5b590",
    });
    tooltipText.value.push({
        label: "Minimum",
        value: data.min,
        bg: "#bbc3c380",
    });

    if (
        chartLegendArray.value.filter((el) => el.label !== "Historical")
            .length > 0
    ) {
        chartLegendArray.value
            .filter((el) => el.label !== "Historical")
            .forEach((year) => {
                const yearIdx = bisect(
                    fetchedYears.value[`year${year.label}`],
                    date
                );
                const data = fetchedYears.value[`year${year.label}`][yearIdx];
                tooltipText.value.push({
                    label: year.label,
                    value: data.v,
                    color: year.color,
                });
            });
    }
};

/**
 * Add mouse events for the chart tooltip and hover, if applicable
 */
const addHoverEvents = () => {
    svg.value.on("mousemove", (ev) => tooltipMouseMove(ev));
    svg.value.on("mouseout", tooltipMouseOut);
    // TODO add hover line or date indicator
};

const addOuterBars = (scale = scaleY.value) => {
    if (outerBars.value) d3.selectAll(".bar.outer").remove();
    outerBars.value = g.value
        .selectAll(".bar.outer")
        .data(formattedChartData.value)
        .enter()
        .append("rect")
        .attr("fill", "#bbc3c380")
        .attr("class", "sdf bar outer streamflow-clipped")
        .attr("x", (d) => scaleX.value(d.d))
        .attr("y", (d) => scale(d.max))
        .attr("width", (d) => width / formattedChartData.value.length)
        .attr("height", (d) => {
            if(d.max > 0 && d.min > 0){
                return Math.abs(scale(d.max - d.min))
            } else {
                return null;
            }
        })
};

const addInnerbars = (scale = scaleY.value) => {
    if (innerBars.value) d3.selectAll(".bar.inner").remove();
    innerBars.value = g.value
        .selectAll(".bar.inner")
        .data(formattedChartData.value)
        .enter()
        .append("rect")
        .attr("fill", "#aab5b580")
        .attr("class", "sdf bar inner streamflow-clipped")
        .attr("x", (d) => scaleX.value(d.d))
        .attr("y", (d) => scale(d.p75))
        .attr("width", (d) => width / formattedChartData.value.length)
        .attr("height", (d) => Math.abs(scale(d.p75) - scale(d.p25)));
};

const addMedianLine = (scale = scaleY.value) => {
    if (medianLine.value) d3.selectAll(".line.median").remove();
    medianLine.value = g.value
        .append("path")
        .datum(formattedChartData.value)
        .attr("fill", "none")
        .attr("stroke", "#999999")
        .attr("stroke-width", 2)
        .attr("class", "sdf line median streamflow-clipped")
        .attr(
            "d",
            d3
                .line()
                .x((d) => scaleX.value(d.d))
                .y((d) => scale(d.p50))
                .defined((d) => d.p50 !== null && d.p50 !== NaN)
        );
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
    const yearLine = g.value
        .append("path")
        .datum(yearData)
        .attr("fill", "none")
        .attr("stroke", year.color)
        .attr("stroke-width", 2)
        .attr("class", "sdf line median streamflow-clipped")
        .attr(
            "d",
            d3
                .line()
                .x((d) => scaleX.value(d.d))
                .y((d) => scale(d.v))
                .defined((d) => d.v !== null && d.v !== 0 && d.v !== NaN)
        );
};

/**
 * flow data consists of a outer/background light grey area, inner darker area, and median line
 * additionally, if the user has selected yearly data, lines are added to the chart for each
 * of the selected years.
 */
const addSevenDayFlowData = async (scale = scaleY.value) => {
    addOuterBars(scale);
    addInnerbars(scale);
    addMedianLine(scale);

    for (const year of chartLegendArray.value.filter(
        (el) => el.label !== "Historical"
    )) {
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
    const foundExistingData = fetchedYears.value.find(
        (el) => el.year === `year${year.label}`
    );
    if (foundExistingData) {
        return foundExistingData;
    } else {
        // if no data exists for the year, get it.
        // API fetch call to go here.
        const data = sevenDayHistorical.map((el) => {
            return {
                d: new Date(
                    new Date(chartStart.value).getUTCFullYear(),
                    0,
                    el.d
                ),
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
        .attr("transform", `translate(0, ${height + 0})`);

    g.value
        .append("text")
        .attr("class", "x axis-label")
        .attr("transform", `translate(${width / 2}, ${height + 35})`)
        .text("Date");
};

const addYaxis = (scale = scaleY.value) => {
    if (gAxisY.value) gAxisY.value.remove();
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
        .text("Flow (m³/s)");
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
 * Sets the key/values in the dataset as desired and days of year to dates.
 * This function may be subject to change as API response content is determined.
 *
 * @param data - the raw data to be formatted.
 */
const formatChartData = (data) => {
    try {
        formattedChartData.value = data.map((el) => {
            return {
                d: new Date(
                    new Date(chartStart.value).getUTCFullYear(),
                    0,
                    el.d
                ),
                max: el.max,
                min: el.min,
                p25: el.p25,
                p50: el.p50,
                p75: el.p75,
            };
        });
    } catch (e) {
        formattedChartData.value = [];
    }
};

/**
 * Determines the start and end date of the chart. Data added to the chart will
 * be formatted to fall within this date range.
 */
const setDateRanges = () => {
    chartStart.value = new Date().setFullYear(
        new Date().getUTCFullYear() - 1,
        0,
        1
    );
    chartEnd.value = new Date().setFullYear(new Date().getUTCFullYear(), 0, -1);
};

const setAxisX = () => {
    // set x-axis scale
    scaleX.value = d3
        .scaleTime()
        .domain([chartStart.value, chartEnd.value])
        .range([0, width])
        .nice();
};

const setAxisY = () => {
    const valsToCheck = [
        d3.max(
            formattedChartData.value.map((d) => {
                d.max;
            })
        ),
    ];

    yMax.value = d3.max(valsToCheck);
    yMax.value *= 1.1;
    yMin.value = 0;

    // Y axis
    // set to yMax
    scaleY.value = d3.scaleLinear()
        .range([height, 0])
        .domain([0, 500])
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
</script>

<style lang="scss">
.seven-day-area {
    .seven-day-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
    
        .yearly-input {
            width: 30%;
        }
    
        .chart-legend {
            width: 70%;
            margin: 0 2rem;
        }
    }
    height: 100%;
}

.seven-day-tooltip {
    position: absolute;
    background-color: rgba(255, 255, 255, 0.95);
    border: 1px solid $light-grey-accent;
    border-radius: 3px;
    display: flex;
    flex-direction: column;
    pointer-events: none;

    .tooltip-header {
        font-size: 18px;
        padding: 0.25em 1em;
    }

    .tooltip-row {
        padding: 0.25em 1em;
    }
}

#streamflow-chart-container {
    height: 90%;
}

.svg-wrap-sdf {
    width: 100%;
    height: 100%;

    .d3-chart {
        width: 100%;
        height: 100%;
    }
}

.dashed{
   stroke-dasharray: 5,6;
}

.x.axis {
    path {
        stroke: black;
    }
}
.x.axis-grid {
    line {
        stroke: rgba(201, 201, 201, 0.90);
    }
}

.y.axis-grid {
    pointer-events: none;

    line {
        stroke: rgba(201, 201, 201, 0.90);
    }
}

// elements clipped by the clip-path rectangle
.streamflow-clipped {
    clip-path: url('#streamflow-box-clip');
}

</style>
