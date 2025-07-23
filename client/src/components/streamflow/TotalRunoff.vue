
<template>
    <h3>Total Runoff</h3>
    <div class="annual-runoff-chart">
        <div class="svg-wrap-tr">
            <svg class="d3-chart-tr">
                <!-- d3 chart content renders here -->
            </svg>
        </div>
    </div>
</template>

<script setup>
import * as d3 from "d3";
import { sciNotationConverter } from '@/utils/chartHelpers.js';
import { monthAbbrList } from '@/utils/dateHelpers.js';
import { computed, onMounted, ref, watch } from 'vue';

const emit = defineEmits(['update-filters']);

const props = defineProps({
    data: {
        type: Array,
        default: () => [],
    },
    dataAll: {
        type: Array,
        default: () => [],
    },
    dimensionFilter: {
        type: Array,
        default: () => ['Jan', 'Dec'],
    },
});

const loading = ref(false);

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
const width = ref(400);
const chartData = ref();
const chartDataAll = ref();
const transition = ref();
const axisTop = ref();

// brush functionality
const brushVar = ref();
const brushEl = ref();
const brushedStart = ref();
const brushedEnd = ref();

// chart constants
const margin = {
    left: 60,
    right: 50,
    top: 30,
    bottom: 50
};

watch(() => props.dimensionFilter, (selection) => {
    setBrush(selection);
});

watch(() => props.data, (newval) => {
    chartData.value = formatData(newval);
    initializeSvg();
});

watch(() => props.dataAll, (newval) => {
    chartDataAll.value = formatData(newval);
    initializeSvg();
});

onMounted(() => {
    initializeSvg();
});

const initializeSvg = () => {
    loading.value = true;
    if (svg.value) {
        d3.selectAll('.g-els.tr').remove();
    }
    svgWrap.value = document.querySelector('.svg-wrap-tr');
    svgEl.value = svgWrap.value.querySelector('svg');
    svg.value = d3.select(svgEl.value)
        .attr("width", width.value + margin.left + margin.right);

    g.value = svg.value.append('g')
        .attr('class', 'g-els tr')
        .attr("transform", `translate(${margin.left}, ${margin.top})`);

    chartData.value = formatData(props.data);
    chartDataAll.value = formatData(props.dataAll);

    width.value = svg.value.attr('width') - margin.left - margin.right;
    height.value = d3.max([(chartDataAll.value.length * (barHeight.value + 1)), 200]);

    svg.value.attr('height', height.value + margin.top + margin.bottom)
    svg.value.attr('width', width.value + margin.right + margin.left)
    
    // set up chart elements
    setAxes();
    addAxes();
    addBars();
    addBrush();
}

const addBars = () => {
    // adjust scales: update x-scale input domain
    const minXVal = d3.min(chartData.value, d => d.value);
    xScale.value.domain([
        d3.max([1, minXVal]),
        d3.max(chartData.value, d => d.value),
    ]).nice();

    // update x-axis
    g.value.select('.axis--x')
        .transition(transition.value)
        .call(axisTop.value)
        .selectAll('text')
        .attr('transform', 'translate(13,-10) rotate(-45)');

    // d3 "data join"
    const bars = g.value.selectAll('.bar')
        .data(chartData.value);

    // enter selection: create new elements
    bars.enter().append('rect')
        .attr('class', 'bar')
        .attr('x', 0)
        .attr('y', d => yScale.value(d.date))
        .attr('height', barHeight.value)
        // update selection: resize bars
        .merge(bars)
        .transition(transition.value)
        .attr('width', d => xScale.value(d.value) || 0);
}

const addBrush = () => {
    brushVar.value = d3.brushY()
        .extent([[0, 0], [width.value, height.value + barHeight.value]])
        .on("end", brushEnded)
    
    brushEl.value = svg.value.append("g")
        .call(brushVar.value)
        .attr('data-cy', 'tr-chart-brush')
        .attr('transform', `translate(${margin.left}, ${margin.top})`)
};

const brushEnded = (event) => {
    if (!event.sourceEvent) return; // Only transition after input.
    // clear filters for empty selection
    if (!event.selection) {
        clearFilters();
        return;
    }

    const s = event.selection;
    const d0 = s.map(yScale.value.invert);
    const d1 = d0.map(d3.timeYear.round);

    // If empty when rounded, use floor & ceil instead.
    if (d1[0] >= d1[1]) {
        d1[0] = d3.timeYear.floor(d0[0]);
        d1[1] = d3.timeYear.offset(d1[0]);
    }

    brushEl.value
        .transition()
        .call(event.target.move, d1.map(yScale.value));

    updateFilters(d1);
}

/**
 * emit null to clear dimension filters
 */
const clearFilters = () => {
    emit('update-filters', null);
};

/**
 * emit an event with a new filter range
 * @param  {Array} dates array with min and max years
 */
const updateFilters = (dates) => {
    const years = dates.map(y => +d3.timeFormat('%Y')(y));
    // "filterRange does not include the top point"
    years[1] += 1; // adjust for crossfilter behavior
    emit('update-filters', years);
};

/**
 * move brush to reflect changed filters
 * pass null to clear brush
 * @param  {Array|null} years params for group.filter method
*/
const setBrush = (selection) => {
    // clear brush on null (no transition)
    if (selection === null) {
        d3.select('.brush.annual-runoff')
            .call(brushVar.value.move, null);
        return;
    }
    // convert years integer to pixel values
    const selectionRange = selection.map((y) => {
        const date = new Date(y, 1, 1);
        return yScale.value(date);
    });
    // move brush
    d3.select('.brush.annual-runoff')
        .transition(transition.value)
        .call(brushVar.value.move, selectionRange);
}

const addAxes = () => {
    g.value.append('g')
        .attr('class', 'axis axis--x')
        .attr('transform', 'translate(0,-3)');

    // left axis
    g.value.append('g')
        .attr('class', 'axis axis--y')
        .attr('transform', 'translate(-2,0)')
        .call(d3.axisLeft(yScale.value)
        .ticks(chartDataAll.value.length, '%Y'));
}

const setAxes = () => {
    xScale.value = d3.scaleSymlog().rangeRound([0, width.value]).clamp(true);
    yScale.value = d3.scaleTime().rangeRound([0, height.value]);
    // transition for bar size and axis
    transition.value = d3.transition().duration(500);
    // set y-scale input domain
    const maxDate = d3.max(chartDataAll.value, d => d.date);
    yScale.value.domain([
        d3.min(chartDataAll.value, d => d.date),
        d3.timeDay.offset(d3.timeYear.offset(maxDate), -1), // end of year
    ]);

    // top axis
    axisTop.value = d3.axisTop(xScale.value)
        .tickSize(6)
        .ticks(2)
        .tickFormat(sciNotationConverter);
}

/**
 * format input data with d3 date objects and adjusted values
 * fills in missing years with null values
 * @param  {Array} input input data from Crossfilter
 * @return {Array}       adjusted data with year, date, & adjusted value
 */
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
    for (let i = firstYear; i < lastYear; i += 1) {
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
</script>

<style lang="scss">
.annual-runoff-chart {
    height: 80vh;
    overflow-y: scroll;
    
    .overlay {
        pointer-events: all;
    }

    .bar {
        fill: steelblue;
    }
}
</style>
