<template>
    <div>
        <h3>Monthly Flow Statistics</h3>
        <div class="flow-duration-container">
            <div id="flow-duration-chart-container">
                <div class="svg-wrap-mf">
                    <svg class="d3-chart-mf">
                        <!-- d3 chart content renders here -->
                    </svg>
                </div>
            </div>

            <div
                v-if="showTooltip"
                class="monthly-flow-tooltip"
                :style="`left: ${tooltipPosition[0]}px; top: ${tooltipPosition[1]}px`"
            >
                <q-card>
                    <div
                        v-for="(key, idx) in Object.keys(tooltipData)"
                        :key="idx"
                    >
                        <div
                            v-if="idx === 0"
                        >
                            <div
                                class="tooltip-header"
                            >
                                <span class="text-h6">{{ tooltipData[key] }}</span>
                                <div>
                                    Discharge (m³/s)
                                </div>
                            </div>
                        </div>
                        <div
                            v-else
                            class="tooltip-row"
                            :class="['Max', 'Median', 'Min'].includes(key) ? 'box-val' : 'val'"
                        >
                            {{ key }}: {{ tooltipData[key].toFixed(2) }}
                        </div>
                    </div>
                </q-card>
            </div>
        </div>
    </div>
</template>

<script setup>
import * as d3 from "d3";
import { monthAbbrList } from '@/utils/dateHelpers.js';
import { onMounted, ref, watch } from 'vue';

const props = defineProps({
    // filtered data from crossfilter group.all()
    data: {
        type: Array,
        required: true,
    },
    startMonth: {
        type: Number,
        default: 0,
    },
    endMonth: {
        type: Number,
        default: 11,
    },
})

// chart variables
const svgWrap = ref();
const svgEl = ref();
const svg = ref();
const g = ref();
const xScale = ref();
const yScale = ref();
const yMax = ref();
const transition = ref();
const localChartData = ref();

// brush functionality
const brush = ref();
const brushEl = ref();

// chart constants
const width = 500;
const height = 300;
const margin = {
    left: 50,
    right: 50,
    top: 10,
    bottom: 50
};

// tooltip
const showTooltip = ref(false);
const tooltipData = ref();
const tooltipPosition = ref();

const emit = defineEmits(['range-selected']);

watch(() => props.data, () => {
    localChartData.value = formatData(props.data);
    initializeSvg();
}, { deep: true });

onMounted(() => {
    localChartData.value = formatData(props.data);
    initializeSvg();
});

const initializeSvg = () => {
    if (svg.value) {
        d3.selectAll('.g-els.mf').remove();
    }
    svgWrap.value = document.querySelector('.svg-wrap-mf');
    svgEl.value = svgWrap.value.querySelector('svg');
    svg.value = d3.select(svgEl.value)
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .attr("transform", `translate(${margin.left}, ${margin.top})`);
    transition.value = d3.transition().duration(500);

    g.value = svg.value.append('g')
        .attr('class', 'g-els sdf')
        .attr("transform", `translate(${margin.left}, ${margin.top})`);

    // set up chart elements
    setAxes();

    // add clip-path element - removing content outside the chart
    const defs = g.value.append('defs');
    defs.append('clipPath')
        .attr('id', 'flow-duration-box-clip')
        .append('rect')
        .attr('width', width)
        .attr('height', height);

    addAxes();
    addBoxPlots();
    addBrush();
    addTooltipHandlers();
}

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
    const date = Math.floor(xScale.value.invert(gX) - 2);
    const foundData = localChartData.value[date];

    if (!foundData) return
    // some custom handling for the tooltip content, depending on their values
    tooltipData.value = {
        'Month': monthAbbrList[date],
        'Max': foundData.max,
        '75th %ile': foundData.p75,
        'Median': foundData.median,
        '25th %ile': foundData.p25,
        'Min': foundData.min
    };
    tooltipPosition.value = [event.pageX - 350, event.pageY - 100];
    showTooltip.value = true;
}

/**
 * Given the current scaling, renders the box plots with
 * min/max/median lines and connecting dotted lines
 *
 * @param scale - the current x and y scales. Can be modified if zoom/pan functionality is desired.
 */
const addBoxPlots = (scale = { x: xScale.value, y: yScale.value }) => {
    d3.selectAll('.mf-boxplot').remove();

    localChartData.value.forEach(month => {
        // add maximum lines
        const padding = 3
        g.value
            .append('line')
            .style('stroke', 'black')
            .style('stroke-width', 2)
            .attr('class', 'mf-boxplot')
            .attr('x1', scale.x(month.key) + padding)
            .attr('y1', scale.y(month.max))
            .attr('x2', scale.x(month.key) + (width / 12) - padding)
            .attr('y2', scale.y(month.max))

        // add max to top of box line
        g.value
            .append('line')
            .style('stroke', 'black')
            .style("stroke-dasharray", "10, 3")
            .style('stroke-width', 2)
            .attr('class', 'mf-boxplot')
            .attr('x1', scale.x(month.key) + (width / 24))
            .attr('y1', scale.y(month.max))
            .attr('x2', scale.x(month.key) + (width / 24))
            .attr('y2', scale.y(month.p75))

        // add box
        g.value
            .append('rect')
            .attr('class', 'mf-boxplot')
            .attr('x', scale.x(month.key) + padding)
            .attr('y', scale.y(month.p75))
            .attr('width', (width / 12) - (2 * padding))
            .attr('height', scale.y(month.p25) - scale.y(month.p75))
            .attr('stroke', 'black')
            .attr('fill', 'steelblue');

        // add median lines
        g.value
            .append('line')
            .style('stroke', 'black')
            .style('stroke-width', 2)
            .attr('class', 'mf-boxplot')
            .attr('x1', scale.x(month.key) + padding)
            .attr('y1', scale.y(month.median))
            .attr('x2', scale.x(month.key) + (width / 12) - padding)
            .attr('y2', scale.y(month.median))

        // add min to bottom of box line
        g.value
            .append('line')
            .style('stroke', 'black')
            .style("stroke-dasharray", "10, 3")
            .style('stroke-width', 2)
            .attr('class', 'mf-boxplot')
            .attr('x1', scale.x(month.key) + (width / 24))
            .attr('y1', scale.y(month.p25))
            .attr('x2', scale.x(month.key) + (width / 24))
            .attr('y2', scale.y(month.min))

        // add minimum lines
        g.value
            .append('line')
            .style('stroke', 'black')
            .style('stroke-width', 2)
            .attr('class', 'mf-boxplot')
            .attr('x1', scale.x(month.key) + padding)
            .attr('y1', scale.y(month.min))
            .attr('x2', scale.x(month.key) + (width / 12) - padding)
            .attr('y2', scale.y(month.min))
            .attr('transform', `translate(0, 0)`)
    })
}

/**
 * format data into a structure with all the values needed for the box plot
 * @param  {Array} input array of objects (from crossfilter group.all)
 * @return {Array}       array of objects with values for box & whisker elements
 */
const formatData = (input) => {
    const output = input.map((e) => {
        // add date object
        const date = e.key;
        // add percentiles
        const valueList = e.value.valueList;
        const p75 = d3.quantile(valueList, 0.75) || 0;
        const p25 = d3.quantile(valueList, 0.25) || 0;
        return {
            key: e.key,
            count: e.value.count,
            max: e.value.max || 0,
            median: e.value.median || 0,
            min: e.value.min || 0,
            p25,
            p75,
            date,
        };
    });

    return output;
};

/**
 * Sets up brush behaviour and handling
 */
const addBrush = () => {
    brush.value = d3.brushX()
        .extent([[0, 0], [width, height]])
        .on("end", brushEnded)

    brushEl.value = svg.value.append("g")
        .call(brush.value)
        .attr('data-cy', 'mfs-chart-brush')
        .attr('transform', `translate(${margin.left}, ${margin.top})`)
}

/**
 * Handler for the brush functionality, executed when the brush is finished drawing.
 * In some cases, like when the user only clicks without brushing, the event may
 * not have all the properties needed to work as expected. Some additional handling
 * has been included here to account for that case.
 *
 * @param event - the brush end event
 */
const brushEnded = (event) => {
    const selection = event.selection;
    if (!event.sourceEvent || !selection) return;
    let [x0, x1] = selection.map(d => Math.floor(xScale.value.invert(d)));
    if (x0 === x1) {
        brushEl.value.call(brush.value.move, [x0, x1 + 1].map(xScale.value));
        emit('range-selected', x0 - 1, Math.min(x1 - 1, 11));
    } else {
        brushEl.value.call(brush.value.move, [x0, x1].map(xScale.value));
        emit('range-selected', x0 - 1, Math.min(x1, 11));
    }
};

watch(() => [props.startMonth, props.endMonth], () => {
    brushEl.value.call(brush.value.move, [props.startMonth, props.endMonth + 1].map(xScale.value));
});

/**
 * Renders the x and y axes onto the chart area.
 *
 * @param scale the current x and y axis scaling
 */
const addAxes = (scale = { x: xScale.value, y: yScale.value }) => {
    d3.selectAll('.mf.axis').remove();
    d3.selectAll('.mf.axis-label').remove();
    // x axis labels and lower axis line
    g.value.append('g')
        .attr('class', 'x axis mf')
        .call(d3.axisBottom(scale.x).tickFormat((d, i) => monthAbbrList[i]))
        .attr('transform', `translate(0, ${height + 0})`)

    g.value.append('text')
        .attr('class', 'x axis-label mf')
        .attr("transform", `translate(${width / 2}, ${height + 35})`)
        .text('Date')

    // x axis labels and lower axis line
    g.value.append('g')
        .attr('class', 'y axis mf')
        .call(d3.axisLeft(scale.y).ticks(5))
        .attr('transform', `translate(0, 0)`)

    g.value.append('text')
        .attr('class', 'y axis-label mf')
        .attr("transform", `translate(-40, ${height / 1.5})rotate(-90)`)
        .text('Monthly Flow (m³/s)')
}

/**
 * Sets the axis properties for x and y axes.
 */
const setAxes = () => {
    // set x-axis scale
    xScale.value = d3.scaleLinear()
        .range([0, width])
        .domain([
            // 2014 - any non-leap year
            1,
            13,
        ]);

    // set y-axis scale
    yMax.value = d3.max(localChartData.value.map(el => el.max));
    yMax.value *= 1.10;

    // Y axis
    yScale.value = d3.scaleLinear()
        .domain([0, yMax.value])
        .range([height, 0])
        .nice();
}
</script>

<style lang="scss">
// elements clipped by the clip-path rectangle
.flow-duration-clipped {
    clip-path: url('#flow-duration-box-clip');
}

.monthly-flow-tooltip {
    position: absolute;
    display: flex;
    width: 10rem;

    .tooltip-header {
        padding: 0.25rem;
    }

    .tooltip-row {
        padding: 0 0.7rem;

        &.box-val {
            color: white;
            background-color: steelblue;
        }
        &.val {
            color: white;
            background-color: rgb(41, 41, 41);
        }
    }
}
</style>
