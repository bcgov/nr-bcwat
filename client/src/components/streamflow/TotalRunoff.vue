
<template>
    <div class="streamflow-chart-runoff">
        <div class="text-h6">Total Runoff</div>
        <div class="annual-runoff-chart">
            <div class="svg-wrap-tr" />
        </div>
        <div
            v-if="showTooltip"
            class="total-runoff-tooltip"
            :style="`left: ${tooltipPosition[0]}px; top: ${tooltipPosition[1]}px`"
        >
            <q-card>
                <div class="tooltip-header">
                    <span class="text-h6">{{ tooltipData['date'].getUTCFullYear() }}</span>
                </div>
                <div class="q-ml-sm">
                    Discharge
                </div>
                <div class="tooltip-row box-val">
                    {{ addCommas(tooltipData['value'].toFixed(0)) }} m³
                </div>
            </q-card>
        </div>
    </div>
</template>

<script setup>
import * as d3 from "d3";
import { addCommas } from "@/utils/stringHelpers.js";
import { sciNotationConverter } from '@/utils/chartHelpers.js';
import { computed, onMounted, ref, watch } from 'vue';
import { Notify } from 'quasar';

const emit = defineEmits(['year-range-selected', 'reset-years']);

const props = defineProps({
    data: {
        type: Array,
        default: () => [],
    },
    dataAll: {
        type: Array,
        default: () => [],
    },
    startYear: {
        type: Number,
        default: 0,
    },
    endYear: {
        type: Number,
        default: 0,
    },
    startMonth: {
        type: Number,
        default: 0,
    },
    endMonth: {
        type: Number,
        default: 11,
    },
});

const loading = ref(false);
const startYear = ref();
const endYear = ref();

// chart variables
const svgEl = ref();
const svg = ref();
const g = ref();
const xScale = ref();
const yScale = ref();
const xMax = ref();
const barHeight = ref(11);
const height = ref(270);
const chartDataAll = ref([]);

const showTooltip = ref(false);
const tooltipPosition = ref([0, 0]);
const tooltipData = ref();

// brush functionality
const brush = ref();
const brushEl = ref();
const brushedStart = ref();
const brushedEnd = ref();

// chart constants
const width = 560;
const margin = {
    left: 60,
    right: 1,
    top: 30,
    bottom: 50
};

watch(() => [props.startYear, props.endYear], () => {
    if ((!props.startYear && !props.endYear) || (props.startYear === props.data[0].key && props.endYear === props.data[props.data.length - 1].key)) {
        brushEl.value.call(brush.value.move, null);
    } else {
        brushEl.value.call(brush.value.move, [new Date(props.startYear, 0, 1), new Date(props.endYear + 1, 0, 1)].map(yScale.value));
    }

    chartDataAll.value = formatData(props.data);
    setAxes();
    addAxes();
    addBars();
});

watch(() => [props.startMonth, props.endMonth], () => {
    chartDataAll.value = formatData(props.data);
    setAxes();
    addAxes();
    addBars();
});

onMounted(() => {
    chartDataAll.value = formatData(props.data);
    initializeTotalRunoff();
});

const formatData = (input) => {
    if (!input.length) {
        return [];
    }
    // fill in any missing years with null values
    const denseArray = [];
    const firstYear = input[0].key;
    const lastYear = input[input.length - 1].key;
    const yearMap = new Map();
    input.forEach((e) => {
        yearMap.set(e.key, e);
    });
    for (let i = firstYear; i <= lastYear; i += 1) {
        const thisYear = yearMap.get(i);
        if (thisYear) {
            denseArray.push(thisYear);
        } else {
            denseArray.push({
                key: i,
                value: null,
            });
        }
    }

    // parse dates and adjust values
    const formatted = denseArray.map((d) => {
        const year = d.key;
        const date = d3.timeParse('%Y')(year);
        const value = (d.value === null) ? null : d.value * 86400; // convert to m3/yr
        return {
            date,
            value,
        };
    });

    return formatted;
};

const initializeTotalRunoff = () => {
    loading.value = true;
    if (svg.value) {
        d3.selectAll('.g-els.tr').remove();
    }
    height.value = d3.max([(props.dataAll.length * (barHeight.value + 5)), 200]);
    svgEl.value = document.querySelector('.svg-wrap-tr');
    svg.value = d3.select(svgEl.value)
        .append('svg')
        .attr("width", "100%")
        .attr("height", "100%")
        .attr("viewBox", `0 0 ${width + 90} ${height.value + 120}`)
        .attr("preserveAspectRatio", "xMidYMid meet");

    g.value = svg.value.append('g')
        .attr('class', 'g-els tr')
        .attr("transform", `translate(${margin.left}, ${margin.top + 20})`);

    // set up chart elements
    setAxes();
    addAxes();
    addBars();
    addBrush();
    addTooltipHandlers();
    loading.value = false;
};

const addBars = () => {
    d3.selectAll('.tr.bar').remove();

    const bars = g.value
        .selectAll('.bar')
        .data(chartDataAll.value)

    // enter selection: create new elements
    bars
        .enter()
        .append('rect')
        .attr('class', 'bar')
        .attr('x', 0)
        .attr('y', d => yScale.value(d.date))
        .attr('height', ((height.value / chartDataAll.value.length) - 2))
        // update selection: resize bars
        .merge(bars)
        .style('fill', 'steelblue')
        .transition()
        .duration(200)
        .attr('width', d => {
            return xScale.value(d.value) || 0
        })
        .style('fill', 'steelblue');
};

const addTooltipHandlers = () => {
    svg.value.on('mousemove', mouseMoved);
    svg.value.on('mouseout', mouseOut);
};

const mouseOut = () => {
    showTooltip.value = false;
}

/**
 * Handle the mouse movement event and invert the chart's pixel coordinates to
 * get the data at that position. This is done to populate the tooltip.
 *
 * @param event mouseEvent from the chart
 */
const mouseMoved = (event) => {
    const [gX, gY] = d3.pointer(event, g.value.node());
    if (gX < 0 || gX > width + margin.right) return;
    if (gY > height.value) return;

    const date = yScale.value.invert(gY);
    const bisect = d3.bisector(d => d.date).left;
    const i = bisect(chartDataAll.value, d3.timeYear.floor(date));
    const yearData = chartDataAll.value[i];

    if (yearData) {
        tooltipData.value = yearData;
        tooltipPosition.value = [event.pageX - 460, event.pageY + 20];
        showTooltip.value = true;
    } else {
        showTooltip.value = false;
    }
}

const addBrush = () => {
    brush.value = d3.brushY()
        .extent([[0, 0], [width, height.value + barHeight.value]])
        .on("end", brushEnded)

    brushEl.value = g.value.append("g")
        .call(brush.value)
        .attr('data-cy', 'tr-chart-brush')
        .attr('class', 'tr-chart-brush')
        .attr('transform', `translate(0, 0)`)
};

const brushEnded = (event) => {
    if(event.sourceEvent?.type === 'mouseup' && event.selection === null){
        emit('reset-years');
    }

    const selection = event.selection;
    if (!event.sourceEvent || !selection || selection[0] < 0) {
        if (selection === null) {
            startYear.value = null;
            endYear.value = null;
            emit('year-range-selected', new Date(props.data[0].d).getUTCFullYear(), new Date(props.data[props.data.length - 1].d).getUTCFullYear());
        }
        return;
    };
    if (!event.sourceEvent) return; // Only transition after input.

    const d0 = selection.map(yScale.value.invert);
    const d1 = d0.map(d3.timeYear.round);
    startYear.value = d0;
    endYear.value = d1;

    // If empty when rounded, use floor & ceil instead.
    if (d1[0] >= d1[1]) {
        d1[0] = d3.timeYear.floor(d0[0]);
        d1[1] = d3.timeYear.offset(d1[0]);
    }

    brushEl.value
        .transition()
        .duration(200)
        .call(brush.value.move, d1.map(yScale.value));

    emit('year-range-selected', d0[0].getUTCFullYear(), d0[1].getUTCFullYear());
};

const addAxes = () => {
    svg.value.selectAll('.x.axis').remove();
    svg.value.selectAll('.y.axis').remove();
    svg.value.selectAll('.y.axis-label').remove();

    // x axis labels and lower axis line
    g.value.append('g')
        .attr('class', 'x axis')
        .call(
            d3.axisTop(xScale.value)
            .ticks(2)
            .tickFormat(sciNotationConverter)
        )
        .selectAll("text")
            .attr("transform", "translate(30, -15)rotate(-30)")
            .style("text-anchor", "end");

    // x axis labels and lower axis line
    g.value.append('g')
        .attr('class', 'y axis')
        .call(
            d3.axisLeft(yScale.value)
            .ticks(props.data.length < 3 ? 1 : props.data.length)
            .tickFormat(d3.timeFormat('%Y'))
        )

    g.value.append('text')
        .attr('class', 'y axis-label')
        .attr("transform", `translate(-40, ${80})rotate(-90)`)
        .text('Runoff (m³)')
};

const setAxes = () => {
    // set x-axis scale
    xMax.value = d3.max(chartDataAll.value.map(el => {
        return el.value;
    }));

    const minXVal = d3.min(chartDataAll.value, d => d.value);

    xScale.value = d3.scaleLog()
        .rangeRound([0, width])
        .clamp(true);

    xScale.value.domain([
        d3.max([1, minXVal]),
        d3.max(chartDataAll.value, d => d.value),
    ]).nice();

    // set y-axis scale
    const maxDate = d3.max(chartDataAll.value.map(el => el.date));
    yScale.value = d3.scaleTime()
        .range([0, height.value])
    yScale.value.domain([
        d3.min(chartDataAll.value.map(el => el.date)), // start of year
        d3.timeDay.offset(d3.timeYear.offset(maxDate), -1), // end of year
    ])
};

</script>

<style lang="scss">
.date-selectors {
    display: flex;
    align-items: center;

    .selector {
        width: 8rem;
    }
}

.annual-runoff-chart {
    height: 75%;
    overflow-y: auto;

    .overlay {
        pointer-events: all;
    }
}

.total-runoff-tooltip {
    position: absolute;
    display: flex;
    flex-direction: column;

    .tooltip-header {
        margin: 0 0.25rem;
    }

    .tooltip-row {
        margin: 0.25rem;
        padding: 0 1rem;

        &.box-val {
            color: white;
            background-color: steelblue;
        }
    }
}

.bar {
    pointer-events: none;
    z-index: 9;
}

.tr-chart-brush, .selection {
    z-index: 10;
}
</style>
