
<template>
    <h3>Total Runoff</h3>
    <div class="date-selectors">
        <q-select 
            :model-value="startYear"
            class="selector"
            label="Year From"
            dense
            :options="dataYears"
            @update:model-value="(newval) => {
                startYear = newval
                onYearRangeUpdate([startYear, endYear])
            }"
        />
        <div class="q-mx-sm">
            -
        </div>
        <q-select 
            :model-value="endYear"
            class="selector q-mx-sm"
            label="Year to"
            dense
            :options="dataYears"
            @update:model-value="(newval) => {
                endYear = newval
                onYearRangeUpdate([startYear, endYear])
            }"
        />
        <q-select 
            :model-value="specifiedMonth"
            class="selector q-mx-sm"
            label="Month"
            dense
            :options="monthAbbrList"
            data-cy="month-selector"
            @update:model-value="(newval) => {
                specifiedMonth = newval;
                emit('month-selected', newval, newval);
            }"
        />
        <q-btn 
            class="text-bold q-mx-sm"
            label="reset dates"
            flat
            color="primary"
            @click="resetDates"
        />
    </div>
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

const emit = defineEmits(['year-range-selected', 'month-selected']);

const props = defineProps({
    data: {
        type: Array,
        default: () => [],
    },
    startEndMonths: {
        type: Array,
        default: () => ['Jan', 'Dec'],
    },
});

const loading = ref(false);
const formattedChartData = ref([]);
const startYear = ref();
const endYear = ref();
const specifiedMonth = ref();

// chart variables
const svgWrap = ref();
const svgEl = ref();
const svg = ref();
const g = ref();
const xScale = ref();
const yScale = ref();
const xMax = ref();
const dataYears = computed(() => {
    if(props.data.length){
        return [...new Set(props.data.map(el => el.year))];
    }
    // arbitrary year
    return [1914];
});
const barHeight = ref(11);
const height = ref(270);

// brush functionality
const brushVar = ref();
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

watch(() => props.startEndMonths, (newval, oldval) => {
    if(JSON.stringify(newval) === JSON.stringify(oldval)) {
        return;
    }
    if(newval[0] === newval[1]){
        specifiedMonth.value = newval[0];
    } else {
        specifiedMonth.value = '';
    }

    setAxes()
    addBars();
});

onMounted(() => {
    initializeTotalRunoff();
});

const onYearRangeUpdate = (yeararr) => {
    if(yeararr[0] && yeararr[1]){
        if(yeararr[0] > yeararr[1]){
            startYear.value = yeararr[0];
            endYear.value = yeararr[0];
            brushedStart.value = yeararr[0];
            brushedEnd.value = yeararr[0];
        } else {
            brushedStart.value = yeararr[0];
            brushedEnd.value = yeararr[1];
        }

        emit('year-range-selected', brushedStart.value, brushedEnd.value);

        if(brushEl.value){
            brushEl.value
                .transition()
                .call(
                    brushVar.value.move, 
                    [yScale.value(brushedStart.value), yScale.value(brushedEnd.value) + barHeight.value]
                );
        }
    }
}

const resetDates = () => {
    loading.value = true;
    startYear.value = null;
    endYear.value = null;
    specifiedMonth.value = '';
    emit('year-range-selected', props.data[0].year, props.data[props.data.length - 1].year);
    emit('month-selected', 'Jan', 'Dec'); // set to full month range
    brushEl.value.remove();
    brushEl.value = svg.value.append("g")
        .call(brushVar.value)
        .attr('transform', `translate(${margin.left}, ${margin.top})`)
    loading.value = false;
}

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
    addBrush();
    loading.value = false;
}

const addBars = () => {
    d3.selectAll('.tr.bar').remove();

    props.data.forEach(year => {
        // TODO: set the sums in the chart based on the provided month ranges
        // const annualSum = year.data.reduce((accumulator, currentValue, currentIndex) => {
        //     if((currentIndex >= monthAbbrList.findIndex(el => el === props.startEndMonths[0])) && (currentIndex <= monthAbbrList.findIndex(el => el === props.startEndMonths[1]))){
        //         return accumulator + currentValue;   
        //     } else {
        //         return accumulator;
        //     }
        // });

        const annualSum = year.value;

        // add box
        const bars = g.value
            .append('rect')
            .attr('class', `tr bar ${year.year}`)
            .attr('x', 0)
            .attr('y', yScale.value(year.year))
            .attr('width', 0)
            .attr('height', (height.value / props.data.length) - 1)

        bars
            .transition()
            .duration(500)
            .attr('class', `tr bar ${year.year}`)
            .attr('x', 0)
            .attr('y', yScale.value(year.year))
            .attr('width', xScale.value(annualSum))
            .attr('height', (height.value / props.data.length) - 1)
            .attr('fill', 'steelblue')
    })
};

const addBrush = () => {
    brushVar.value = d3.brushY()
        .extent([[0, 0], [width, height.value + barHeight.value * 2]])
        .on("end", brushEnded)
    
    brushEl.value = svg.value.append("g")
        .call(brushVar.value)
        .attr('data-cy', 'tr-chart-brush')
        .attr('transform', `translate(${margin.left}, ${margin.top})`)
}

const brushEnded = (event) => {
    const selection = event.selection;
    if (!event.sourceEvent || !selection || selection[0] < 0){
        if(selection === null){
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
            brushVar.value.move, 
            [yScale.value(y0), yScale.value(y1) + barHeight.value]
        );
}

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
}

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
        .domain([props.data[0].year, props.data[props.data.length - 1].year])
}

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
</style>
