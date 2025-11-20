<template>
    <div>
        <div class="chart-area">
            <div id="climate-chart-container">
                <div :id="`climate-${props.chartId}-chart`" class="svg-wrap">
                    <svg class="d3-chart">
                        <!-- d3 chart content renders here -->
                    </svg>
                </div>
            </div>
        </div>
        <div class="chart-legend">
            <div class="flex">
                <span>Normal / Historical Average</span>
                <div
                    class="legend-line"
                    :style="{ 'background-color': props.lineColor }"
                ></div>
            </div>
            <div class="flex">
                <span>Projected Average for 2050s</span>
                <div
                    class="legend-box"
                    :style="{ 'background-color': props.areaColor }"
                ></div>
            </div>
        </div>
        <div
            v-if="tooltipData"
            class="watershed-report-tooltip"
            :style="`top: ${tooltipPosition[1]}px; left: ${tooltipPosition[0]}px;`"
        >
            <h3 class="q-ma-none">{{ monthAbbrList[tooltipData?.group] }}</h3>
            <table>
                <tbody>
                    <tr>
                        <td>Normal / Historical Average:</td>
                        <td>
                            {{ tooltipData?.normal.toFixed(2) }}
                            {{ chartUnits }}
                        </td>
                    </tr>
                    <tr>
                        <td>Min Projected Average for 2050s:</td>
                        <td>
                            {{ tooltipData?.min.toFixed(2) }}
                            {{ chartUnits }}
                        </td>
                    </tr>
                    <tr>
                        <td>Max Projected Average for 2050s:</td>
                        <td>
                            {{ tooltipData?.max.toFixed(2) }}
                            {{ chartUnits }}
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>

<script setup>
import { monthAbbrList } from "@/utils/dateHelpers";
import { computed, onMounted, ref } from "vue";
import * as d3 from "d3";

const props = defineProps({
    chartData: {
        type: Object,
        default: () => {},
    },
    chartId: {
        type: String,
        default: "",
    },
    areaColor: {
        type: String,
        default: "",
    },
    lineColor: {
        type: String,
        default: "",
    },
});

const margin = { top: 20, right: 20, bottom: 30, left: 60 };
let width = 400;
let height = 200;
const svg = ref(null);
const svgEl = ref();
const svgWrap = ref();
const g = ref();
const xAxisScale = ref();
const yAxisScale = ref();
const tooltipData = ref(null);
const tooltipPosition = ref([0, 0]);

const chartUnits = computed(() => {
    return props.chartId === "temperature" ? "°C" : "mm";
});

const formattedChartData = computed(() => {
    const myData = [];
    monthAbbrList.forEach((__, idx) => {
        myData.push({
            group: idx,
            normal: props.chartData.historical[idx],
            min: props.chartData.future[idx].min,
            max: props.chartData.future[idx].max,
        });
    });

    return myData;
});

const minY = computed(() => {
    let minValue = 999;
    formattedChartData.value.forEach((month) => {
        minValue = Math.min(minValue, month.min, month.normal);
    });
    return minValue;
});
const maxY = computed(() => {
    let maxValue = -999;
    formattedChartData.value.forEach((month) => {
        maxValue = Math.max(maxValue, month.max, month.normal);
    });
    return maxValue;
});

onMounted(async () => {
    window.addEventListener("resize", updateChart);
    await updateChart();
});

const updateChart = async () => {
    // const myElement = document.getElementById(`climate-${props.chartId}-chart`);
    
    if (svg.value) {
        svg.value.selectAll(".g-els").remove();
    }

    // set the data from selections to align with the chart range
    await waitForElementToExist(`#climate-${props.chartId}-chart`).then(() => {
        svgWrap.value = document.querySelector(`#climate-${props.chartId}-chart`);
    });
    svgEl.value = svgWrap.value.querySelector("svg");

    svg.value = d3
        .select(svgEl.value)
    svg.value.attr('viewBox', `300 -20 350 250`);

    g.value = svg.value
        .append("g")
        .attr("class", "g-els")
        .attr("transform", `translate(${margin.left}, ${margin.top})`);

    if (svgWrap.value) {
        width = svgWrap.value.clientWidth - margin.left - margin.right;
        height = svgWrap.value.clientHeight - margin.top - margin.bottom - 50;
    }

    // build the chart axes
    setXAxis();
    setYAxis();

    // add clip-path element
    const defs = g.value.append("defs");
    defs.append("clipPath")
        .attr("id", "box-clip")
        .append("rect")
        .attr("width", width)
        .attr("height", height)
        .attr('transform', 'translate(0, 0)');

    addChartData();
    bindTooltipHandlers();
}

const addChartData = () => {
    // Plot the area
    g.value
        .append("path")
        .datum(formattedChartData.value)
        .attr("fill", props.areaColor)
        .attr('class', `${props.chartId}-projected`)
        .attr(
            "d",
            d3
                .area()
                .x((d) => xAxisScale.value(d.group))
                .y0((d) => yAxisScale.value(d.min))
                .y1((d) => yAxisScale.value(d.max))
                .curve(d3.curveBasis)
        );

    g.value
        .append("path")
        .datum(formattedChartData.value)
        .attr("fill", "none")
        .attr('class', `${props.chartId}-normal`)
        .attr("stroke", props.lineColor)
        .attr("stroke-width", 1.5)
        .attr(
            "d",
            d3
                .line()
                .x((d) => xAxisScale.value(d.group))
                .y((d) => yAxisScale.value(d.normal))
                .curve(d3.curveBasis)
        );
}

const setXAxis = () => {
    // Add X axis
    xAxisScale.value = d3
        .scaleLinear()
        .domain([0, 11])
        .range([0, width]);
    g.value
        .append("g")
        .attr("transform", `translate(0, ${height})`)
        .style('font-family', '"BC Sans", sans-serif')
        .call(
            d3
                .axisBottom(xAxisScale.value)
                .tickFormat((_, i) => monthAbbrList[i])
        );
}

const setYAxis = () => {
    // Add Y axis
    yAxisScale.value = d3
        .scaleLinear()
        .domain([minY.value, maxY.value])
        .range([height, 0]);

    g.value.append("g").call(d3.axisLeft(yAxisScale.value));

    // Add Y axis label
    g.value
        .append("text")
        .attr("text-anchor", "end")
        .attr("fill", "#5d5e5d")
        .attr("y", 6)
        .attr("dx", "-1.5em")
        .attr("dy", "-3em")
        .attr("transform", "rotate(-90)")
        .style('font-family', '"BC Sans", sans-serif')
        .text(`${props.chartId[0].toUpperCase()}${props.chartId.slice(1)} (${chartUnits.value})`);
}

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
    const [gX, gY] = d3.pointer(event, svg.value.node());
    if (gX < margin.left || gX > width + margin.right) return;
    if (gY > height + margin.top) return;
    const date = xAxisScale.value.invert(gX - 1);
    tooltipData.value = formattedChartData.value[Math.floor(date)];
    tooltipPosition.value = [event.pageX - 50, event.pageY - 150];
};

/**
 * When the mouse leaves the svg, set the text to blank. This hides the tooltip
 */
const tooltipMouseOut = () => {
    tooltipData.value = null;
};

/**
 * helper function to wait for the element to be exist in the DOM
 * 
 * @param selector html selector
 */
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

.chart-area {
    display: flex;
    justify-content: center;
    width: 100%;

    #climate-chart-container {
        width: 100%;

        .svg-wrap {
            width: 100%;

            .d3-chart {
                width: 100%;
                height: 15rem;
            }
        }
    }
}
</style>
