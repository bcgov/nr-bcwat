
<template>
    <h3>Total Runoff</h3>
    <div class="date-selectors">
        <q-select 
            v-model="startYear"
            class="selector"
            label="Year From"
            dense
        />
        <div class="q-mx-sm">
            -
        </div>
        <q-select 
            v-model="endYear"
            class="selector q-mx-sm"
            label="Year to"
            dense
        />
        <q-select 
            v-model="specifiedMonth"
            class="selector q-mx-sm"
            label="Month"
            dense
        />
        <q-btn 
            class="text-bold q-mx-sm"
            label="reset dates"
            flat
            color="primary"
            @click="() => {}"
        />
    </div>
    <div class="annual-runoff-chart">
            <div class="svg-wrap-mf">
                <svg class="d3-chart-mf">
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

const emit = defineEmits(['year-range-selected']);

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
const brushedYearStart = ref();
const brushedYearEnd = ref();
const brush0 = ref();
const brush1 = ref();

// chart constants
const width = 400;
const margin = {
    left: 60,
    right: 50,
    top: 30,
    bottom: 50
};

watch(() => props.startEndMonths, () => {
    processData(props.data);
    initializeMonthlyFlowChart();
})

onMounted(() => {
    console.log('mount')
    initializeMonthlyFlowChart();
});

const initializeMonthlyFlowChart = () => {
    loading.value = true;
    if (svg.value) {
        d3.selectAll('.g-els.mf').remove();
    }
    processData(props.data);
    
    svgWrap.value = document.querySelector('.svg-wrap-mf');
    svgEl.value = svgWrap.value.querySelector('svg');
    svg.value = d3.select(svgEl.value)
        .attr("width", width + margin.left + margin.right)
    g.value = svg.value.append('g')
        .attr('class', 'g-els mf')
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

    const bars = g.value.selectAll('.mf.bar')
        .data(yearTotals)
        .join('rect')
        .attr('x', 0)
        .attr('y', d => yScale.value(d.d))
        .attr('width', 0)
        .attr('height', () => height.value / formattedChartData.value.length)

    bars
        .transition()
        .duration(500)
        .attr('class', 'mf bar')
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
    
    brushEl.value = g.value.append("g")
        .call(brushVar.value)
}

const brushEnded = (event) => {
    const selection = event.selection;
    if (!event.sourceEvent || !selection || selection[0] < 0 || selection[0] > height.value) return;
    const [y0, y1] = selection.map(d => {
        return Math.floor(yScale.value.invert(d))
    });

    brushedYearStart.value = y0;
    brushedYearEnd.value = y1;

    emit('range-selected', brushedYearStart.value, brushedYearEnd.value);

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
