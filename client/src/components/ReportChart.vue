<template>
    <div
        class="chart-area"
        data-cy="report-chart-area"
    >
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
                        yearlyData = newval ? newval.sort() : [];
                        updateChartLegendContents();
                    }
                "
            />
            <q-btn label="Download PNG" icon="mdi-download" outline @click="downloadPng()"/>
        </div>

        <div id="chart-container">
            <div class="svg-wrap">
                <svg class="d3-chart">
                    <!-- d3 chart content renders here -->
                </svg>
            </div>
        </div>
        <p>Data may be from a live sensor and has not gone through QA, so may contain errors.</p>
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
                        {{ tip.label }}:&nbsp;
                    </span>
                    <span>{{ parseFloat(tip.value).toFixed(2) }}{{ props.chartOptions.units }}</span>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import * as d3 from "d3";
import { monthAbbrList } from "@/utils/dateHelpers.js";
import {
    getStreamflowReportDataByYear,
    getGroundwaterLevelReportDataByYear,
    getClimateReportDataByYear
} from '@/utils/api.js';
import { ref, computed, onMounted, watch, onBeforeUnmount } from "vue";

const props = defineProps({
    chartData: {
        type: Object,
        default: () => {},
    },
    historicalChartData: {
        type: Array,
    },
    chartType: {
        type: String,
        default: '',
    },
    chartName: {
        type: String,
        default: ''
    },
    chartOptions: {
        type: Object,
        default: () => ({
            name: '',
            startYear: null,
            endYear: null,
            legend: [{ label: '', color: '', }],
            chartColor: '#b3d4fc',
            yLabel: '',
            units: '',
        }),
    },
    activePoint: {
        type: Object,
        default: () => {},
    },
    yearlyType: {
        type: String,
        default: '',
    }
});

const colorScale = [
    "#2196F3",
    "#4CAF50",
    "#9C27B0",
    "#795548",
    "#FF80AB",
    "#00897B",
    "#AFB42B",
    "#00BCD4",
    "#FF9800",
];

const chartLegendArray = ref([]);
const yearlyData = ref([]);
const colors = ref(null);

// chart sizing
const margin = ref({
    top: 70,
    right: 50,
    bottom: 30,
    left: 65,
});
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
const currentLine = ref();
const medianArea = ref();
const hoverLine = ref(null);
const hoverLinePath = ref(null);
const scaleX = ref();
const scaleY = ref();
const gAxisY = ref();
const gGridX = ref();
const gGridY = ref();
let zoom;

watch(() => props.chartData, () => {
    updateChart();
});

watch(() => yearlyData.value, (newVal, oldVal) => {
    // fetch data for the newly added year only
    const diff = newVal.filter((x) => !oldVal.includes(x));
    // TODO make API fetch call for the data for the newly added year
    updateChart();
});

/**
 * determine which years of data are available for the point
 */
const yearlyDataOptions = computed(() => {
    try{
        return Array(props.chartOptions.endYear - props.chartOptions.startYear + 1).fill().map((_, idx) => props.chartOptions.startYear + idx);
    } catch(e) {
        return [];
    }
});

onMounted(() => {
    window.addEventListener("resize", updateChart);
    updateChartLegendContents();
    updateChart();
});

onBeforeUnmount(() => {
    window.removeEventListener("resize", updateChart);
    if (svg.value) svg.value.selectAll("*").remove();
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
        })
    });

    chartLegendArray.value.push(...props.chartOptions.legend);

    if (props.chartOptions.name !== 'temperature') {
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
        color: "#bbc3c380",
    });
    chartLegendArray.value.push({
        label: "Historical 10th %",
        color: "#bbc3c380",
    });
};

/**
 * calls the component functions to build the chart and set its data
 */
const init = async () => {
    if (svg.value) {
        d3.selectAll(".g-els").remove();
    }

    // set the data from selections to align with the chart range
    setDateRanges();
    await waitForElementToExist('.svg-wrap').then(() => {
        svgWrap.value = document.querySelector('.svg-wrap');
    });
    svgEl.value = svgWrap.value.querySelector("svg");

    svg.value = d3
        .select(svgEl.value)
        .attr("width", width + margin.value.left + margin.value.right)
        .attr("height", height + margin.value.top + margin.value.bottom)

    svg.value.append("rect")
        .attr("width", "100%")
        .attr("height", "100%")
        .attr("fill", "white");

    g.value = svg.value
        .append("g")
        .attr("class", "g-els")
        .attr("transform", `translate(${margin.value.left}, ${margin.value.top})`);

    if (svgWrap.value) {
        width = svgWrap.value.clientWidth - margin.value.left - margin.value.right;
        height = svgWrap.value.clientHeight - margin.value.top - margin.value.bottom - 50;
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
        .attr("height", height)
        .attr('transform', 'translate(0, 0)');

    addXaxis();
    addYaxis();
    addChartData();
    addYearlyData();
    addHoverEvents();
    defineZoom();
};

const addYearlyData = async (scale = scaleY.value) => {
    for (const year in yearlyData.value) {
        if (!Object.keys(fetchedYears.value).includes(`year${yearlyData.value[year]}`)) {
            const yearData = await getYearlyData(props.activePoint.id, yearlyData.value[year]);
            // set up data
            const yearChartData = [];
            let i = 0;
            for (let d = new Date(chartStart.value); d <= new Date(chartEnd.value); d.setDate(d.getDate() + 1)) {
                const day = Math.floor((d - new Date(d.getFullYear(), 0, 0)) / 1000 / 60 / 60 / 24);
                const dataLength = yearData[props.chartName].length;
                const dataPoint = yearData[props.chartName][day % dataLength];
                yearChartData.push({
                    d: new Date(d),
                    v: dataPoint.v,
                });
                i++;
            }
            fetchedYears.value[`year${yearlyData.value[year]}`] = yearChartData;
            addYearLine(yearlyData.value[year], yearChartData, scale);
        } else {
            addYearLine(yearlyData.value[year], fetchedYears.value[`year${yearlyData.value[year]}`], scale);
        }

    }
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
        .attr("transform", `translate(${margin.value.left}, ${margin.value.top})`)
        .call(zoom);
};

const zoomed = (event) => {
    if (props.chartOptions.name === "manual-snow") return
    tooltipMouseOut();
    const newY = event.transform.rescaleY(scaleY.value);
    const newScaleY = newY.domain(event.transform.rescaleY(scaleY.value).domain());

    zoomElements({ newScaleY });
};

const zoomElements = (newScaleObj) => {
    addYaxis(newScaleObj.newScaleY);
    addChartData(newScaleObj.newScaleY);
    addYearlyData(newScaleObj.newScaleY);
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

    if (gX > width / 2) {
        tooltipPosition.value[0] -= 340
    }

    addTooltipText(gX - 2);

    // Add line where the user is hovering
    if (hoverLine.value) {
        hoverLine.value.remove();
    }

    const date = scaleX.value.invert(gX + margin.value.left);
    hoverLine.value = svg.value.append('g').attr('class', 'hovered')

    hoverLinePath.value = hoverLine.value.append('line')
        .attr('class', 'hovered dashed clipped')
        .attr('x1', scaleX.value(date) - 2)
        .attr('y1', margin.value.top)
        .attr('x2', scaleX.value(date) - 2)
        .attr('y2', height + margin.value.top)
        .attr('stroke', '#444')
        .attr('stroke-width', '2')
};

const addTooltipText = (pos) => {
    const date = scaleX.value.invert(pos);
    const bisect = d3.bisector((d) => new Date(d.d)).center;
    const idx = bisect(props.chartData, date);
    const data = props.chartData[idx];
    const historicalData = props.historicalChartData[idx];

    tooltipText.value.push({
        label: "Date",
        value: `${monthAbbrList[new Date(date).getMonth()]} ${new Date(date).getDate()} ${new Date(date).getFullYear()}`,
    });

    if (props.chartOptions.name === 'temperature') {
        tooltipText.value.push({
            label: "Current Max",
            value: data.currentMax,
            bg: props.chartOptions.chartColor,
        });
        tooltipText.value.push({
            label: "Current Min",
            value: data.currentMin,
            bg: props.chartOptions.chartColor,
        });
    } else if (props.chartOptions.name === 'precipitation') {
        tooltipText.value.push({
            label: "Current",
            value: data.currentMax,
            bg: props.chartOptions.chartColor,
        });
    } else if (props.chartOptions.name === 'snow-on-ground') {
        tooltipText.value.push({
            label: "Current Snow Depth",
            value: data.currentMax,
            bg: props.chartOptions.chartColor,
        });
    } else if (props.chartOptions.name === 'snow-water') {
        tooltipText.value.push({
            label: "Current Snow Water Equiv.",
            value: data.currentMax,
            bg: props.chartOptions.chartColor,
        });
    } else {
        console.log(props.chartOptions)
        tooltipText.value.push({
            label: "Current",
            value: data.v,
            bg: "#FFA500",
        });
    }

    if (historicalData) {
        if ('max' in historicalData) {
            tooltipText.value.push({
                label: "Historical Maximum",
                value: historicalData.max,
                bg: "#bbc3c380",
            });
        }
        if ('p90' in historicalData) {
            tooltipText.value.push({
                label: "Historical 90th Percentile",
                value: historicalData.p90,
                bg: "#aab5b590",
            });
        }
        if ('p75' in historicalData) {
            tooltipText.value.push({
                label: "Historical 75th Percentile",
                value: historicalData.p75,
                bg: "#aab5b590",
            });
        }
        if ('v' in historicalData) {
            tooltipText.value.push({
                label: "Current",
                value: historicalData.v,
                bg: "orange",
            });
        }
        else if ('p50' in historicalData) {
            tooltipText.value.push({
                label: "Historical Median",
                value: historicalData.p50,
                bg: "#99999980",
            });
        }
        if ('p25' in historicalData) {
            tooltipText.value.push({
                label: "Historical 25th Percentile",
                value: historicalData.p25,
                bg: "#aab5b590",
            });
        }
        if ('p10' in historicalData) {
            tooltipText.value.push({
                label: "Historical 10th Percentile",
                value: historicalData.p10,
                bg: "#aab5b590",
            });
        }
        if ('min' in historicalData) {
            tooltipText.value.push({
                label: "Historical Minimum",
                value: historicalData.min,
                bg: "#bbc3c380",
            });
        }
    } else {
        if ('max' in data) {
            tooltipText.value.push({
                label: "Historical Maximum",
                value: data.max,
                bg: "#bbc3c380",
            });
        }
        if ('p75' in data) {
            tooltipText.value.push({
                label: "Historical 75th Percentile",
                value: data.p75,
                bg: "#aab5b590",
            });
        }
        if ('v' in data) {
            tooltipText.value.push({
                label: "Current",
                value: data.v,
                bg: "orange",
            });
        }
        else if ('p50' in data) {
            tooltipText.value.push({
                label: "Historical Median",
                value: data.p50,
                bg: "#99999980",
            });
        }
        if ('p25' in data) {
            tooltipText.value.push({
                label: "Historical 25th Percentile",
                value: data.p25,
                bg: "#aab5b590",
            });
        }
        if ('min' in data) {
            tooltipText.value.push({
                label: "Historical Minimum",
                value: data.min,
                bg: "#bbc3c380",
            });
        }
    }

    if (chartLegendArray.value.filter(el => !isNaN(el.label)).length > 0) {
        chartLegendArray.value.filter(el => !isNaN(el.label)).forEach((year) => {
            const yearIdx = bisect(
                fetchedYears.value[`year${year.label}`],
                date
            );
            const data = fetchedYears.value[`year${year.label}`][yearIdx];
            tooltipText.value.push({
                label: `${year.label} Daily Mean`,
                value: data.v,
                bg: year.color,
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
};

const addOuterBars = (scale = scaleY.value) => {
    if (outerBars.value) d3.selectAll(".bar.outer").remove();
    outerBars.value = g.value
        .selectAll(".bar.outer")
        .data(props.historicalChartData)
        .enter()
        .append("rect")
        .attr("fill", "#bbc3c380")
        .attr("class", "bar outer chart-clipped")
        .attr("x", (d) => scaleX.value(d.d))
        .attr("y", (d) => {
            if ('min' in d) return scale(d.min);
            if ('minavg' in d) return scale(d.minavg);
        })
        .attr("width", width / props.chartData.length)
        .attr("height", (d) => {
            if ('max' in d && 'min' in d) return Math.abs(scale(d.min) - scale(d.max));
            if ('maxavg' in d && 'minavg' in d) return Math.abs(scale(d.minavg) - scale(d.maxavg));
        });
};

const addInnerbars = (scale = scaleY.value) => {
    const data = props.historicalChartData.filter(el => el.p75);
    if (data.length === 0) return;
    if (innerBars.value) d3.selectAll(".bar.inner").remove();
    innerBars.value = g.value
        .selectAll(".bar.inner")
        .data(props.historicalChartData)
        .enter()
        .append("rect")
        .attr("fill", "#aab5b580")
        .attr("class", "bar inner chart-clipped")
        .attr("x", (d) => scaleX.value(d.d))
        .attr("y", (d) => scale(d.p25))
        .attr("width", (d) => width / props.chartData.length)
        .attr("height", (d) => Math.abs(scale(d.p25) - scale(d.p75)));
};

const addMedianLine = (scale = scaleY.value) => {
    if (medianLine.value) d3.selectAll(".line.median").remove();
    medianLine.value = g.value
        .append("path")
        .datum(props.historicalChartData)
        .attr("fill", "none")
        .attr("stroke", "#999999")
        .attr("stroke-width", 2)
        .attr("class", "line median chart-clipped")
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
        .attr("fill", `${props.chartOptions.chartColor}80`)
        .attr("stroke", props.chartOptions.chartColor)
        .attr("stroke-width", 2)
        .attr("class", "area current chart-clipped")
        .attr("d", d3
            .area()
            .x((d) => scaleX.value(d.d))
            .y0((d) => scale(d.currentMin))
            .y1((d) => scale(d.currentMax))
            .curve(d3.curveBasis)
            .defined((d) => d.currentMax !== null && d.currentMin !== null)
        );
};

const addManualSnow = (scale = scaleY.value) => {
    if (outerBars.value) d3.selectAll(".line.outer").remove();
    outerBars.value = g.value
        // .selectAll(".line.outer")
        .datum(props.chartData.filter(el => el.max > 0))
        // .enter()
        .append("path")
        .attr("class", "line outer")
        .attr("fill", "#bbc3c380")
        .attr(
            "d",
            d3
                .area()
                .x((d) => scaleX.value(d.d))
                .y0((d) => scale(d.min))
                .y1((d) => scale(d.max))
                // .curve(d3.curveBasis)
        );
    if (innerBars.value) d3.selectAll(".line.inner").remove();
    innerBars.value = g.value
        .append("path")
        .datum(props.chartData.filter(el => el.max > 0))
        // .selectAll(".line.inner")
        .attr("class", "line inner")
        .attr("fill", "#aab5b580")
        .attr(
            "d",
            d3
                .area()
                .x((d) => scaleX.value(d.d))
                .y0((d) => scale(d.p25))
                .y1((d) => scale(d.p75))
                // .curve(d3.curveBasis)
        );
    if (medianLine.value) d3.selectAll(".line.manual").remove();
    medianLine.value = g.value
        .append("path")
        .datum(props.chartData.filter(el => el.max > 0))
        // .selectAll(".line.manual")
        .attr("class", "line manual")
        .attr("fill", "none")
        .attr("stroke", "#999999")
        .attr("stroke-width", 1.5)
        .attr(
            "d",
            d3
                .line()
                .x((d) => scaleX.value(d.d))
                .y((d) => scale(d.p50))
                // .curve(d3.curveBasis)
        );

    if (medianLine.value) d3.selectAll(".dots").remove();
    addDots("p50", "#999");
    addDots("p75", "#aab5b5");
    addDots("p25", "#aab5b5");
    addDots("max", "#aab5b5");
    addDots("min", "#aab5b5");
};

const addDots = (key, color) => {
    g.value.append("g")
        .selectAll()
        .data(props.chartData.filter(el => el[key]))
        .enter()
        .append("circle")
        .attr("class", "dots")
        .attr("cx", (d) => scaleX.value(d.d))
        .attr("cy", (d) => scaleY.value(d[key]))
        .attr("fill", color)
        .attr("r", 3);
}

const addTodayLine = () => {
    if (medianLine.value) {
        d3.selectAll(".line.today").remove();
        d3.selectAll(".rect.today").remove();
        d3.selectAll(".text.today").remove();
    }
    g.value
        .append("line")
        .attr("class", "line today chart-clipped")
        .attr("x1", scaleX.value(new Date()))
        .attr("y1", 0)
        .attr("x2", scaleX.value(new Date()))
        .attr("y2", height)
        .style("stroke-width", 2)
        .style("stroke", "#000");
    g.value
        .append("rect")
        .attr("class", "rect today chart-clipped")
        .attr("x", scaleX.value(new Date()) - 48)
        .attr("y", -16 + height / 2)
        .style("border-radius", "30px")
        .attr("width", '96px')
        .attr("height", '32px')
        .style("fill", "#FFA500");
    g.value
        .append("text")
        .attr("class", "text today chart-clipped")
        .attr("x", scaleX.value(new Date()))
        .attr("dx", "-43px")
        .attr("y", height / 2)
        .attr("dy", ".35em")
        .text(new Date().toLocaleDateString(undefined, { year: "numeric", month: "short", day: "2-digit"}))
        .style("fill", "white")
        .style("font-weight", "bold")
        .style('font-family', '"BC Sans", sans-serif')
        .style('font-size', '14px')
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
    d3.selectAll(`.year${year}`).remove();

    g.value
        .append("path")
        .datum(yearData)
        .attr("fill", "none")
        .attr("stroke", chartLegendArray.value.find(el => el.label === year).color)
        .attr("stroke-width", 2)
        .attr("class", `line historical chart-clipped year${year}`)
        .attr("d", d3
            .line()
            .x((d) => {
                return scaleX.value(d.d)
            })
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
    // snow chart has a specific implementation
    if (props.chartOptions.name === 'manual-snow') {
        addManualSnow(scale);
    } else {
        if (props.historicalChartData && props.historicalChartData.length) {
            if (('max' in props.historicalChartData[0] && 'min' in props.historicalChartData[0]) || ('maxavg' in props.historicalChartData[0] && 'minavg' in props.historicalChartData[0])) addOuterBars(scale);
            if (('p75' in props.historicalChartData[0] && 'p25' in props.historicalChartData[0]) || ('p90' in props.historicalChartData[0] && 'p10' in props.historicalChartData[0])) addInnerbars(scale);
            if ('p50' in props.historicalChartData[0]) addMedianLine(scale);
        }
    }
    if (props.chartData && 'currentMin' in props.chartData[0] && 'currentMax' in props.chartData[0]) addCurrentArea(scale);
    addTodayLine();
    if (props.chartData && props.chartData.length) {
        addCurrentLine(scale);
    }
};

const addCurrentLine = (scale = scaleY.value) => {
    if (currentLine.value) d3.selectAll(".line.current").remove();

    currentLine.value = g.value
        .append("path")
        .datum(props.chartData)
        .attr("fill", "none")
        .attr("stroke", 'orange')
        .attr("stroke-width", 2)
        .attr("class", "line current chart-clipped")
        .attr("d", d3
            .line()
            .x((d) => scaleX.value(d.d))
            .y((d) => scale(d.v))
            .defined((d) => d.v !== null && d.v !== NaN)
        );
}

/**
 * Retrieves and formats the yearly data for a given year.
 *
 * @param year - the given year for which we must fetch its associated historical data
 * returns a set of dates and values for the current year to display in the chart.
 */
const getYearlyData = async (id, year) => {
    if (props.yearlyType === 'streamflow') {
        return await getStreamflowReportDataByYear(id, year, props.chartType);
    } else if (props.yearlyType === 'climate') {
        return await getClimateReportDataByYear(id, year, props.chartType);
    } else if (props.yearlyType === 'groundwaterlevel') {
        return await getGroundwaterLevelReportDataByYear(id, year, props.chartType);
    } else {
        return [];
    }
};

const addXaxis = (scale = scaleX.value) => {
    if (gGridX.value) g.value.selectAll(".x").remove();
    gGridX.value = g.value
        .append("g")
        .attr("class", "x axis-grid")
        .attr('stroke-opacity', 0.5)
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
        .text("Date")
        .style('font-family', '"BC Sans", sans-serif')
        .style('font-size', '14px')

    // Add legend to top
    let x = 0;
    let y = 25;

    const fullLength = chartLegendArray.value.reduce((accumulator, currentValue) => {
        return accumulator + 55 + (6.5 * `${currentValue.label}`.length)
    }, 0);
    // TODO: adjust margin as needed for larger legends
    // margin.value.top = 40 + (25 * parseInt(fullLength / width))
    chartLegendArray.value.forEach(el => {
        g.value
            .append("rect")
            .attr("transform", `translate(${x}, ${y - 12 - margin.value.top})`)
            .attr("width", 30)
            .attr("height", 15)
            .attr("fill", el.color)
            .attr("stroke", "#000")
            .attr("stroke-width", 2)
        x += 35
        g.value
            .append("text")
            .attr("class", "x axis-label")
            .attr("transform", `translate(${x}, ${y - margin.value.top})`)
            .text(el.label)
            .style('font-family', '"BC Sans", sans-serif')
            .style('font-size', '14px')
        x += 20 + (6.5 * `${el.label}`.length);
        if (x > width * 0.9) {
            x = 0;
            y += 25;
        }
    });
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
        .call(yAxisGrid)
        .attr('stroke-opacity', 0.5)

    g.value
        .append("text")
        .attr("class", "y axis-label")
        .attr("transform", `translate(-50, ${height / 2})rotate(-90)`)
        .text(props.chartOptions.yLabel)
        .style('font-family', '"BC Sans", sans-serif')
        .style('font-size', '14px')
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
    let currentMax = d3.max(props.chartData.map(el => {
        if ('max' in el) {
            return el.max;
        }
        if ('v' in el) {
            return el.v;
        }
    }));

    if (props.historicalChartData) {
        currentMax = d3.max([
            currentMax,
            d3.max(props.historicalChartData.map(el => {
                if (props.chartOptions.name !== 'temperature') {
                    return el.max;
                } else {
                    return el.maxavg;
                }
            })),
        ]);
    }

    let currentMin = 0;
    if (props.chartOptions.name === 'temperature') {
        currentMin = d3.min(props.chartData.map(el => Math.min(el.currentMin, el.min)));
        if (props.historicalChartData) {
            currentMin = d3.min([
                currentMin,
                d3.min(props.historicalChartData.map(el => {
                    return el.minavg;
                })),
            ]);
        }
    }

    // Y axis
    if (props.chartName === 'hydrograph') {
        scaleY.value = d3.scaleLinear().range([0, height]).domain([currentMin, currentMax * 2]);
    } else {
        scaleY.value = d3.scaleLinear().range([height, 0]).domain([currentMin, currentMax * 2]);
    }
};

/**
 * Ensures the chart dimensions and content are resized when the windows is adjusted
 */
const updateChart = () => {
    // timeout catches some potential rendering issues.
    setTimeout(() => {
        init();
    }, 250);
};

const downloadPng = async () => {
    // Select the first svg element
    const svg = d3.select(".d3-chart").node();
    const dataHeader = 'data:image/svg+xml;charset=utf-8';
    // serializer function
    const serializeAsXML = el => (new XMLSerializer()).serializeToString(el);
    const encodeAsUTF8 = serializedStr => `${dataHeader},${encodeURIComponent(serializedStr)}`;
    // encoded svg string
    const svgData = encodeAsUTF8(serializeAsXML(svg))

    const loadImage = async url => {
        const img = document.createElement('img')
        img.src = url
        return new Promise((resolve, reject) => {
            img.onload = () => resolve(img)
            img.onerror = reject
            img.src = url
        })
    }

    const img = await loadImage(svgData);

    const canvas = document.createElement('canvas');
    canvas.width = svg.clientWidth;
    canvas.height = svg.clientHeight;
    canvas.getContext('2d').drawImage(img, 0, 0, svg.clientWidth, svg.clientHeight);
    const dataURL = canvas.toDataURL('image/png', 1.0);

    // perform programmatic download
    const link = document.createElement("a");
    link.download = `${props.chartOptions.name}-${props.activePoint.name}.png`;
    link.href = dataURL;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
};

const waitForElementToExist = (selector) => {
    return new Promise(resolve => {
        if (document.querySelector(selector)) {
            return resolve(document.querySelector(selector));
        }

        const observer = new MutationObserver(() => {
            if (document.querySelector(selector)) {
                observer.disconnect();
                resolve(document.querySelector(selector));
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    });
};
</script>

<style lang="scss">
.chart-area {
    display: flex;
    flex-direction: column;
    height: 100vh;

    .hovered {
        pointer-events: none;
    }

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

        .svg-wrap {
            width: 100%;
            height: 100%;

            .d3-chart {
                width: 100%;
                height: 100%;
            }
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
            stroke: rgba(201, 201, 201);
        }
        .domain {
            stroke-opacity: 0;
        }
    }

    .y.axis-grid {
        pointer-events: none;

        line {
            stroke: rgba(201, 201, 201);
        }
        .domain {
            stroke-opacity: 0;
        }
    }

}

// elements clipped by the clip-path rectangle
.chart-clipped {
    clip-path: url("#box-clip");
}
</style>
