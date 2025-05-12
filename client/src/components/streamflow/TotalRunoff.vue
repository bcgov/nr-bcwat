
<template>
    <h3>Total Runoff</h3>
    <div class="date-selectors">
        <q-select 
            :model-value="startYear"
            class="selector"
            label="Year From"
            dense
            :options="dataYears.map(el => el.year)"
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
            :options="dataYears.map(el => el.year)"
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
import { onMounted, ref, watch } from 'vue';

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
const dataYears = ref([1914]);
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

watch(() => props.startEndMonths, (monthRangeArr) => {
    if(monthRangeArr[0] === monthRangeArr[1]){
        specifiedMonth.value = monthRangeArr[0]
    } else {
        specifiedMonth.value = '';
    }

    processData(props.data);
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
    emit('year-range-selected', formattedChartData.value[0].year, formattedChartData.value[formattedChartData.value.length - 1].year);
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
    processData(props.data);
    
    svgWrap.value = document.querySelector('.svg-wrap-tr');
    svgEl.value = svgWrap.value.querySelector('svg');
    svg.value = d3.select(svgEl.value)
        .attr("width", width + margin.left + margin.right)
    g.value = svg.value.append('g')
        .attr('class', 'g-els tr')
        .attr("transform", `translate(${margin.left}, ${margin.top})`);

    height.value = d3.max([(formattedChartData.value.length * (barHeight.value + 1)), 200]);

    svg.value.attr('height', height.value + margin.top + margin.bottom)
    svg.value.attr('width', width + margin.right + margin.left)
    
    // set up chart elements
    setAxes();
    addAxes();
    addBars();
    setTimeout(() => {
        addBrush();
    })
    loading.value = false;
}

const addBars = () => {
    d3.selectAll('.tr.bar').remove();

    // add box
    const yearTotals = formattedChartData.value.map(year => {
        if(year.data.length > 0){
            return {
                d: year.year,
                v: year.data.reduce((acc, curr) => acc + curr)
            };
        } else {
            return {
                d: year.year,
                v: 0
            };
        }
    })

    const bars = g.value.selectAll('.tr.bar')
        .data(yearTotals)
        .join('rect')
        .attr('class', 'tr bar')
        .attr('x', 0)
        .attr('y', d => yScale.value(d.d))
        .attr('width', 0)
        .attr('height', () => height.value / formattedChartData.value.length)

    bars
        .transition()
        .duration(500)
        .attr('class', 'tr bar')
        .attr('x', 0)
        .attr('y', d => yScale.value(d.d) + 1)
        .attr('width', d => xScale.value(d.v))
        .attr('height', () => (height.value / formattedChartData.value.length) - 2)
        .attr('fill', 'steelblue')
};

const addBrush = () => {
    brushVar.value = d3.brushY()
        .extent([[0, 0], [width, height.value + barHeight.value]])
        .on("end", brushEnded)
    
    brushEl.value = svg.value.append("g")
        .call(brushVar.value)
        .attr('transform', `translate(${margin.left}, ${margin.top})`)
}

const brushEnded = (event) => {
    const selection = event.selection;

    if (!event.sourceEvent || !selection || selection[0] < 0 || selection[0] > height.value){
        if(selection === null){
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
            .ticks(formattedChartData.value.length)
            .tickFormat(d3.format('d'))
        )

    g.value.append('text')
        .attr('class', 'y axis-label')
        .attr("transform", `translate(-40, ${80})rotate(-90)`)
        .text('Runoff (m³)')
}

const setAxes = () => {
    const total = dataYears.value.map(year => {
        if(year.data.length > 0){
            return year.data.reduce((acc, curr) => acc + curr)
        } else {
            return 0;
        }
    });

    // set y-axis scale
    xMax.value = d3.max(total);

    // set x-axis scale
    xScale.value = d3.scaleLinear()
        .domain([0, xMax.value])
        .range([0, width])

    yScale.value = d3.scaleLinear()
        .range([0, height.value])
        .domain([formattedChartData.value[0].year, formattedChartData.value[formattedChartData.value.length - 1].year])
}

const processData = (rawData) => {
    dataYears.value = [];
    const start = new Date(rawData[0].d).getUTCFullYear();
    const end = new Date(rawData[rawData.length - 1].d).getUTCFullYear();

    for(let i = start; i <= end; i++){
        dataYears.value.push({
            year: i,
            data: [], 
        });
    }

    const startMonthIdx = monthAbbrList.findIndex(el => el === props.startEndMonths[0]);
    const endMonthIdx = monthAbbrList.findIndex(el => el === props.startEndMonths[1]);

    rawData.forEach(entry => {
        const year = new Date(entry.d).getUTCFullYear();
        const foundYear = dataYears.value.find(el => el.year === year);

        if(!foundYear){
            dataYears.value.push({
                d: new Date(entry.d),
                data: [ entry.v ? entry.v : 0 ]
            })
        } else {
            if(new Date(entry.d).getUTCMonth() >= startMonthIdx && new Date(entry.d).getUTCMonth() <= endMonthIdx){
                foundYear.data.push(entry.v);
            } else {
                foundYear.data.push(0.00);
            }

        }
    });

    formattedChartData.value = dataYears.value;
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
