<template>
    <div class="streamflow-chart">
        <div class="text-h6">Monthly Flow Statistics</div>
        <div class="monthly-flow-stats-container">
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
import { sciNotationConverter } from '@/utils/chartHelpers.js';
import { onMounted, ref, watch, nextTick } from 'vue';

const props = defineProps({
    // filtered data from crossfilter group.all()
    data: {
        type: Array,
        required: true,
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
    specifiedMonth: {
        type: [Number, String],
        default: 'All'
    }
})

// chart variables
const svgWrap = ref();
const svgEl = ref();
const svg = ref();
const g = ref();
const xScale = ref();
const yScale = ref();
const yMax = ref();
const yMin = ref();
const transition = ref();
const localChartData = ref();
const boxPlotMax = ref();
const boxPlotMaxLine = ref();
const boxPlotMin = ref();
const boxPlotMinLine = ref();
const boxPlotMedian = ref();
const boxPlotRect = ref();

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

const emit = defineEmits(['range-selected', 'reset-months']);

watch(() => [props.startYear, props.endYear], () => {
    localChartData.value = formatData(props.data);
    updateChart();
});

watch(() => props.specifiedMonth, (newval) => {
    if(newval === null || newval === undefined){ 
        return;
    };
    if(newval === 'All') {
        brushEl.value
            .transition()
            .duration(200)
            .call(brush.value.move, [0, 0]);
        emit('reset-months');
        return;
    }
    const monthIdx = monthAbbrList.findIndex(el => el === newval);
    brushEl.value
        .transition()
        .duration(200)
        .call(brush.value.move, [xScale.value(monthIdx), xScale.value(monthIdx + 1)]);
}, { deep: true });

onMounted(() => {
    localChartData.value = formatData(props.data);
    window.addEventListener("resize", () => {
        d3.selectAll('.mf-boxplot').remove();
        initializeSvg();
    });
    initializeSvg();
    addBrush();
});

const initializeSvg = () => {
    if (svg.value) {
        d3.selectAll('.g-els.mf').remove();
    }
    svgWrap.value = document.querySelector('.svg-wrap-mf');
    svgEl.value = svgWrap.value.querySelector('svg');
    svg.value = d3.select(svgEl.value)
        .attr("width", "100%")
        .attr("height", height + margin.top + margin.bottom)
        .attr("transform", `translate(${margin.left}, ${margin.top})`);
    transition.value = d3.transition().duration(500);

    g.value = svg.value.append('g')
        .attr('class', 'g-els sdf')
        .attr("transform", `translate(${margin.left}, ${margin.top})`);

    // set up chart elements
    setAxes();
    addAxes();
    setTimeout(() => {
        addBoxPlots();
    });
    addTooltipHandlers();
};

const updateChart = () => {
    setAxes();
    addAxes();
    updateBoxPlots();
}

const addTooltipHandlers = () => {
    svg.value.on('mousemove', mouseMoved);
    svg.value.on('mouseout', mouseOut);
};

const mouseOut = () => {
    showTooltip.value = false;
};

/**
 * Handle the mouse movement event and invert the chart's pixel coordinates to
 * get the data at that position. This is done to populate the tooltip.
 *
 * @param event mouseEvent from the chart
 */
const mouseMoved = (event) => {
    const [gX, gY] = d3.pointer(event, svg.value.node());
    if (gX < 0 || gX > width + margin.right) return;
    if (gY > height + margin.top) return;
    const date = xScale.value.invert(gX - margin.left);
    const bisect = d3.bisector((d) => d.date).left;
    const idx = bisect(localChartData.value, date);
    const data = localChartData.value[idx];

    if(!data) return;
    // some custom handling for the tooltip content, depending on their values
    tooltipData.value = {
        'Month': monthAbbrList[data.date - 1],
        'Max': data.max,
        '75th %ile': data.p75,
        'Median': data.median,
        '25th %ile': data.p25,
        'Min': data.min
    };

    tooltipPosition.value = [event.pageX - 270, event.pageY + 15];
    showTooltip.value = true;
};

const updateBoxPlots = (scale = { x: xScale.value, y: yScale.value }) => {
    localChartData.value.forEach(month => {
        const boxPlotMaxLocal = d3.selectAll(`.mf-boxplot-max-${month.key}`)
        const boxPlotMaxLineLocal = d3.selectAll(`.mf-boxplot-max-line-${month.key}`)
        const boxPlotMinLocal = d3.selectAll(`.mf-boxplot-min-${month.key}`)
        const boxPlotMinLineLocal = d3.selectAll(`.mf-boxplot-min-line-${month.key}`)
        const boxPlotMedianLocal = d3.selectAll(`.mf-boxplot-median-${month.key}`)
        const boxPlotRectLocal = d3.selectAll(`.mf-boxplot-rect-${month.key}`)

        const padding = 3
        boxPlotMaxLocal
            .transition(200)
            .attr('x1', scale.x(month.key - 1) + padding)
            .attr('y1', scale.y(month.max))
            .attr('x2', scale.x(month.key - 1) + (width / 12) - padding)
            .attr('y2', scale.y(month.max))

        boxPlotMaxLineLocal
            .transition(200)
            .attr('x1', scale.x(month.key - 1) + (width / 24))
            .attr('y1', scale.y(month.max))
            .attr('x2', scale.x(month.key - 1) + (width / 24))
            .attr('y2', scale.y(month.p75))

        boxPlotMedianLocal
            .transition(200)
            .attr('x1', scale.x(month.key - 1) + padding)
            .attr('y1', scale.y(month.median))
            .attr('x2', xScale.value(month.key - 1) + (width / 12) - padding)
            .attr('y2', yScale.value(month.median))

        boxPlotMinLineLocal
            .transition(200)
            .attr('x1', xScale.value(month.key - 1) + (width / 24))
            .attr('y1', yScale.value(month.p25))
            .attr('x2', xScale.value(month.key - 1) + (width / 24))
            .attr('y2', yScale.value(month.min))

        boxPlotMinLocal
            .transition(200)
            .attr('x1', xScale.value(month.key - 1) + padding)
            .attr('y1', yScale.value(month.min))
            .attr('x2', xScale.value(month.key - 1) + (width / 12) - padding)
            .attr('y2', yScale.value(month.min))

        boxPlotRectLocal
            .transition(200)
            .attr('x', scale.x(month.key - 1) + padding)
            .attr('y', scale.y(month.p75))
            .attr('width', (width / 12) - (2 * padding))
            .attr('height', scale.y(month.p25) - scale.y(month.p75))     
    })
}

/**
 * Given the current scaling, renders the box plots with
 * min/max/median lines and connecting dotted lines
 *
 * @param scale - the current x and y scales. Can be modified if zoom/pan functionality is desired.
 */
const addBoxPlots = (scale = { x: xScale.value, y: yScale.value }) => {
    localChartData.value.forEach(month => {
        // add maximum lines
        const padding = 3
        g.value
            .append('line')
            .style('stroke', 'black')
            .style('stroke-width', 1)
            .attr('class', `mf-boxplot mf-boxplot-max-${month.key}`)
            .attr('x1', scale.x(month.key - 1) + padding)
            .attr('y1', scale.y(month.max))
            .attr('x2', scale.x(month.key - 1) + (width / 12) - padding)
            .attr('y2', scale.y(month.max))

        // add max to top of box line
        g.value
            .append('line')
            .style('stroke', 'black')
            .style("stroke-dasharray", "10, 3")
            .style('stroke-width', 1)
            .attr('class', `mf-boxplot mf-boxplot-max-line-${month.key}`)
            .attr('x1', scale.x(month.key - 1) + (width / 24))
            .attr('y1', scale.y(month.max))
            .attr('x2', scale.x(month.key - 1) + (width / 24))
            .attr('y2', scale.y(month.p75))

        // add box
        g.value
            .append('rect')
            .attr('class', `mf-boxplot mf-boxplot-rect-${month.key}`)
            .style('z-index', 1)
            .attr('x', scale.x(month.key - 1) + padding)
            .attr('y', scale.y(month.p75))
            .attr('width', (width / 12) - (2 * padding))
            .attr('height', scale.y(month.p25) - scale.y(month.p75))
            .attr('fill', 'steelblue')

        // add median lines
        g.value
            .append('line')
            .style('stroke', 'black')
            .style('stroke-width', 1)
            .attr('class', `mf-boxplot mf-boxplot-median-${month.key}`)
            .attr('x1', scale.x(month.key - 1) + padding)
            .attr('y1', scale.y(month.median))
            .attr('x2', scale.x(month.key - 1) + (width / 12) - padding)
            .attr('y2', scale.y(month.median))

        // add min to bottom of box line
        g.value
            .append('line')
            .style('stroke', 'black')
            .style("stroke-dasharray", "10, 3")
            .style('stroke-width', 1.)
            .attr('class', `mf-boxplot mf-boxplot-min-line-${month.key}`)
            .attr('x1', scale.x(month.key - 1) + (width / 24))
            .attr('y1', scale.y(month.p25))
            .attr('x2', scale.x(month.key - 1) + (width / 24))
            .attr('y2', scale.y(month.min))

        // add minimum lines
        g.value
            .append('line')
            .style('stroke', 'black')
            .style('stroke-width', 1)
            .attr('class', `mf-boxplot mf-boxplot-min-${month.key}`)
            .attr('x1', scale.x(month.key - 1) + padding)
            .attr('y1', scale.y(month.min))
            .attr('x2', scale.x(month.key - 1) + (width / 12) - padding)
            .attr('y2', scale.y(month.min))
    })
};

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

    brushEl.value = g.value.append("g")
        .call(brush.value)
        .attr('class', 'mfs-chart-brush')
        .attr('data-cy', 'mfs-chart-brush')
        .attr('transform', `translate(0, 0)`)
};

/**
 * Handler for the brush functionality, executed when the brush is finished drawing.
 * In some cases, like when the user only clicks without brushing, the event may
 * not have all the properties needed to work as expected. Some additional handling
 * has been included here to account for that case.
 *
 * @param event - the brush end event
 */
const brushEnded = (event) => {
    if(event.sourceEvent?.type === 'mouseup' && event.selection === null){
        emit('reset-months');
    }

    const selection = event.selection;
    if (!event.sourceEvent || !selection) {
        return;
    };
    let [x0, x1] = selection.map(d => Math.round(xScale.value.invert(d)));
    // place the start of the brush at the start month, end of brush 
    // at that month plus 1 to select the full month width
    brushEl.value
        .transition()
        .duration(selection ? 200 : 0)
        .call(brush.value.move, [xScale.value(x0), xScale.value(x1)]);

    emit('range-selected', x0, x1);
};

/**
 * Renders the x and y axes onto the chart area.
 *
 * @param scale the current x and y axis scaling
 */
const addAxes = (scale = { x: xScale.value, y: yScale.value }) => {
    d3.selectAll('.mf.axis').remove();
    d3.selectAll('.mf.axis-label').remove();
    d3.selectAll('.mf.axis-dates').remove();
    d3.selectAll('.mf.axis-grid').remove();

    // x axis labels and lower axis line
    g.value.append('g')
        .attr('class', 'x axis mf')
        .call(
            d3.axisBottom(scale.x)
            .tickFormat('')
        )
        .attr('transform', `translate(0, ${height + 0})`)

    g.value.append('g')
        .attr('class', 'x axis-dates mf')
        .call(
            d3.axisBottom(scale.x)
            .tickFormat((d, i) => monthAbbrList[i])
        )
        .attr('transform', `translate(${(width / 12) / 2}, ${height + 0})`)

    g.value.append('text')
        .attr('class', 'x axis-label mf')
        .attr("transform", `translate(${width / 2}, ${height + 35})`)
        .text('Date')
        
    // add y axis grid lines
    g.value.append('g')
        .attr('class', 'y axis-grid mf')
        .call(
            d3.axisLeft(yScale.value)
                .tickSize(-width)
                .ticks(3)
                .tickFormat('')
        )

    // y axis labels and lower axis line
    g.value.append('g')
        .attr('class', 'y axis mf')
        .style('z-index', -1)
        .call(
            d3.axisLeft(scale.y)
                .ticks(3)
                .tickFormat(d => sciNotationConverter(d))
        )
        .attr('transform', `translate(0, 0)`)

    g.value.append('text')
        .attr('class', 'y axis-label mf')
        .attr("transform", `translate(-40, ${height / 1.5})rotate(-90)`)
        .text('Monthly Flow (m³/s)')
};

/**
 * Sets the axis properties for x and y axes.
 */
const setAxes = () => {
    // set x-axis scale
    xScale.value = d3.scaleLinear()
        .range([0, width])
        .domain([
            0,
            12,
        ]);

    // set y-axis scale
    yMax.value = d3.max(localChartData.value.map(el => el.max));
    yMax.value *= 1.10;
    yMin.value = d3.min(localChartData.value.map(el => el.min));

    // Y axis
    yScale.value = d3.scaleLog().rangeRound([height, 0]).clamp(true);
    yScale.value.domain([
        yMin.value < 0.001 ? 0.001 : yMin.value, // use dataAll, don't change domain
        // use dataAll, don't change domain
        d3.max([0.001, yMax.value]),
    ]).nice();
};
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
    pointer-events: none;

    .tooltip-header {
        padding: 0.25rem;
    }

    .tooltip-row {
        padding: 0 0.7rem;

        &.box-val {
            color: white;
            background-color: rgb(41, 41, 41);
        }
        &.val {
            color: black;
            background-color: steelblue;
        }
    }
}

.axis-dates {
    line {
        stroke: none;
    }
    path {
        stroke: none;
    }
}

.mf-boxplot {
    pointer-events: none;
}

.axis-grid {
    opacity: 0.5;
    pointer-events: none;
}
</style>
