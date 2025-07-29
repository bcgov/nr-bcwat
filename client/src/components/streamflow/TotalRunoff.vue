
<template>
    <div>
        <h3>Total Runoff</h3>
        <div class="annual-runoff-chart">
            <div class="svg-wrap-tr">
                <svg class="d3-chart-tr">
                    <!-- d3 chart content renders here -->
                </svg>
            </div>
        </div>
        <div
            v-if="showTooltip"
            class="total-runoff-tooltip"
            :style="`left: ${tooltipPosition[0]}px; top: ${tooltipPosition[1]}px`"
        >
            <q-card>
                <div class="tooltip-header">
                    <span class="text-h6">{{ tooltipData['key'] }}</span>
                </div>
                <div class="q-ml-sm">
                    Discharge
                </div>
                <div class="tooltip-row box-val">
                    {{ tooltipData['value'].toFixed(0) }} m<sup>3</sup>
                </div>
            </q-card>
        </div>
    </div>
</template>

<script setup>
import * as d3 from "d3";
import { sciNotationConverter } from '@/utils/chartHelpers.js';
import { onMounted, ref, watch } from 'vue';

const emit = defineEmits(['year-range-selected']);

const props = defineProps({
    data: {
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
});

const loading = ref(false);
const startYear = ref();
const endYear = ref();

// chart variables
const svgWrap = ref();
const svgEl = ref();
const svg = ref();
const g = ref();
const xScale = ref();
const yScale = ref();
const xMax = ref();
const barHeight = ref(11);
const height = ref(270);

const showTooltip = ref(false);
const tooltipPosition = ref([0, 0]);
const tooltipData = ref();

// brush functionality
const brush = ref();
const brushEl = ref();
const brushedStart = ref();
const brushedEnd = ref();

// chart constants
const width = 400;
const margin = {
    left: 60,
    right: 50,
    top: 30,
    bottom: 50
};

watch(() => props.data, () => {
    setAxes();
    addBars();
});

watch(() => [props.startYear, props.endYear], () => {
    if (!props.startYear && !props.endYear) {
        brushEl.value.call(brush.value.move, null);
        return;
    }
    brushEl.value.call(brush.value.move, [props.startYear, props.endYear + 1].map(yScale.value));
});

onMounted(() => {
    initializeTotalRunoff();
});

const initializeTotalRunoff = () => {
    loading.value = true;
    if (svg.value) {
        d3.selectAll('.g-els.tr').remove();
    }

    svgWrap.value = document.querySelector('.svg-wrap-tr');
    svgEl.value = svgWrap.value.querySelector('svg');
    svg.value = d3.select(svgEl.value)
        .attr("width", width + margin.left + margin.right)
    g.value = svg.value.append('g')
        .attr('class', 'g-els tr')
        .attr("transform", `translate(${margin.left}, ${margin.top})`);

    height.value = d3.max([(props.data.length * (barHeight.value + 1))]);

    svg.value.attr('height', height.value + margin.top + margin.bottom)
    svg.value.attr('width', width + margin.right + margin.left)

    // set up chart elements
    setAxes();
    addAxes();
    addBars();
    addTooltipHandlers();
    addBrush();
    loading.value = false;
};

const addBars = () => {
    d3.selectAll('.tr.bar').remove();

    props.data.forEach(year => {
        // add box
        const bars = g.value
            .append('rect')
            .attr('class', `tr bar ${year.key}`)
            .attr('x', 0)
            .attr('y', yScale.value(year.key))
            .attr('width', 0)
            .attr('height', (height.value / props.data.length) - 1)

        bars
            .transition()
            .duration(500)
            .attr('class', `tr bar ${year.key}`)
            .attr('x', 0)
            .attr('y', yScale.value(year.key))
            .attr('width', xScale.value(year.value))
            .attr('height', (height.value / props.data.length) - 1)
            .attr('fill', 'steelblue')
    })
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
    const [gX, gY] = d3.pointer(event, svg.value.node());
    if (gX < margin.left || gX > width + margin.right) return;
    if (gY > height + margin.top) return;

    const mouseIndex = Math.floor(yScale.value.invert(gY) - 2)
    const hoveredYearData = props.data.find(el => el.key === mouseIndex);
    if (hoveredYearData) {
        tooltipData.value = hoveredYearData;
        tooltipPosition.value = [event.pageX - 350, event.pageY - 100];
        showTooltip.value = true;
    } else {
        showTooltip.value = false;
    }
}

const addBrush = () => {
    brush.value = d3.brushY()
        .extent([[0, 0], [width, height.value + barHeight.value * 2]])
        .on("end", brushEnded)

    brushEl.value = svg.value.append("g")
        .call(brush.value)
        .attr('data-cy', 'tr-chart-brush')
        .attr('transform', `translate(${margin.left}, ${margin.top})`)
};

const brushEnded = (event) => {
    const selection = event.selection;
    if (!event.sourceEvent || !selection || selection[0] < 0) {
        if (selection === null) {
            startYear.value = null;
            endYear.value = null;
            emit('year-range-selected', new Date(props.data[0].d).getUTCFullYear(), new Date(props.data[props.data.length - 1].d).getUTCFullYear());
        }
        return;
    };
    const [y0, y1] = selection.map(d => {
        return Math.floor(yScale.value.invert(d))
    });

    // set the brush start and end values
    brushedStart.value = y0;
    brushedEnd.value = y1;

    // also update the selectable fields
    startYear.value = y0;
    endYear.value = y1;

    emit('year-range-selected', brushedStart.value, brushedEnd.value);

    brushEl.value
        .transition()
        .call(
            brush.value.move,
            [yScale.value(y0), yScale.value(y1) + barHeight.value]
        );
};

const addAxes = () => {
    // x axis labels and lower axis line
    g.value.append('g')
        .attr('class', 'x axis')
        .call(
            d3.axisTop(xScale.value)
            .ticks(3)
            .tickFormat(sciNotationConverter)
    )

    // x axis labels and lower axis line
    g.value.append('g')
        .attr('class', 'y axis')
        .call(
            d3.axisLeft(yScale.value)
            .ticks(props.data.length < 3 ? 1 : props.data.length)
            .tickFormat(d3.format('d'))
        )

    g.value.append('text')
        .attr('class', 'y axis-label')
        .attr("transform", `translate(-40, ${80})rotate(-90)`)
        .text('Runoff (m³)')
};

const setAxes = () => {
    // set y-axis scale
    xMax.value = d3.max(props.data.map(el => {
        return el.value;
    }));

    // set x-axis scale
    xScale.value = d3.scaleLinear()
        .domain([0, xMax.value])
        .range([0, width])

    yScale.value = d3.scaleLinear()
        .range([0, height.value])
        .domain([props.data[0].key, props.data[props.data.length - 1].key])
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
    height: 80vh;
    overflow-y: scroll;

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
</style>
