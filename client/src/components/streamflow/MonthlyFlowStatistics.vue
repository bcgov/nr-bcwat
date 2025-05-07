
<template>
    <h3>Total Runoff</h3>
    <div class="date-selectors">
        <q-select 
            class="selector"
            label="Year From"
            dense
        />
        <div class="q-mx-sm">
            -
        </div>
        <q-select 
            class="selector q-mx-sm"
            label="Year to"
            dense
        />
        <q-select 
            class="selector q-mx-sm"
            label="Month"
            dense
        />
        <q-btn 
            class="text-bold q-mx-sm"
            label="reset dates"
            flat
            color="primary"
        />
    </div>
    <div class="monthly-flow-container">
        <div id="monthly-flow-chart-container">
            <div class="svg-wrap-mf">
                <svg class="d3-chart-mf">
                    <!-- d3 chart content renders here -->
                </svg>
            </div>
        </div>
    </div>
</template>

<script setup>
import * as d3 from "d3";
import { monthAbbrList } from '@/constants/dateHelpers.js';
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

const monthDataArr = ref([]);
const loading = ref(false);
const monthPercentiles = ref([]);
const formattedChartData = ref([]);

// chart variables
const svgWrap = ref();
const svgEl = ref();
const svg = ref();
const g = ref();
const xScale = ref();
const yScale = ref();
const xGrid = ref();
const yGrid = ref();
const xAxis = ref();
const yAxis = ref();
const xMax = ref();
const yearRangeArr = ref([1914, 2022]);
const dataYears = ref([1914]);

// brush functionality
const brushVar = ref();
const brushEl = ref();
const brushedYearStart = ref();
const brushedYearEnd = ref();

// chart constants
const width = 400;
const height = 700;
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
    loading.value = true;
    initializeMonthlyFlowChart();
    loading.value = false;
});

const initializeMonthlyFlowChart = () => {
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

    // set up chart elements
    setAxes();
    addAxes();
    addBrush();
    addBars();
}

const addBars = () => {
    // add box
    dataYears.value.forEach(year => {
        const yearDataTotal = year.data.reduce((acc, curr) => acc + curr)

        g.value
            .append('rect')
            .attr('x', 0)
            .attr('y', yScale.value(new Date(year.d).getUTCFullYear()))
            .attr('width', xScale.value(yearDataTotal))
            .attr('height', yScale.value.bandwidth())
            .attr('stroke', 'black')
            .attr('fill', 'steelblue');
    })
};

const addBrush = () => {
    brushVar.value = d3.brushY()
        .extent([[0, 0], [width, height]])
        .on("end", brushEnded)
        .on("start", (ev) => {
            if(ev.selection[0] === ev.selection[1]){
                emit('year-range-selected', monthAbbrList[0], monthAbbrList[monthAbbrList.length - 1])
            }
        })
    
    brushEl.value = g.value.append("g")
        .call(brushVar.value);
}

const brushEnded = (event) => {
    const selection = event.selection;
    if (!event.sourceEvent || !selection) return;

    const [y0, y1] = selection.map(d => {
        return scaleBandInvert(yScale.value)(d)
    });

    brushedYearStart.value = y0;
    brushedYearEnd.value = y1;

    emit('year-range-selected', brushedYearStart.value, brushedYearEnd.value);

    brushEl.value
        .transition()
        .call(
            brushVar.value.move, 
            [yScale.value(y0), yScale.value(y1)]
        );
}

const scaleBandInvert = (scale) => {
    let domain = scale.domain().reverse();
    var paddingOuter = scale(domain[0]);
    var eachBand = scale.step();
    return (val) => {
        var index = Math.floor((val - paddingOuter) / eachBand);
        return domain[Math.max(0, Math.min(index, domain.length - 1))];
    };
};


const addAxes = () => {
    // x axis labels and lower axis line
    g.value.append('g')
        .attr('class', 'x axis')
        .call(
            d3.axisTop(xScale.value)
    )

    // x axis labels and lower axis line
    g.value.append('g')
        .attr('class', 'y axis')
        .call(
            d3.axisLeft(yScale.value)
        )
        .attr('transform', `translate(0, 0)`)

    g.value.append('text')
        .attr('class', 'y axis-label')
        .attr("transform", `translate(-40, ${80})rotate(-90)`)
        .text('Runoff (m³)')
}

const setAxes = () => {
    const total = dataYears.value.map(year => {
        return year.data.reduce((acc, curr) => acc + curr)
    });

    // set y-axis scale
    xMax.value = d3.max(total);
    xMax.value *= 1.10;

    // set x-axis scale
    xScale.value = d3.scaleSymlog()
        .domain([0, xMax.value])
        .range([0, width])

    // Y axis displaying the years in reverse, descending
    yScale.value = d3.scaleBand()
        .range([height, 0])
        .domain(formattedChartData.value.map(el => new Date(el.d).getUTCFullYear()).reverse())
        .padding(0.2)
}

const processData = (rawData) => {
    dataYears.value = [];
    rawData.forEach(entry => {
        const year = new Date(entry.d).getUTCFullYear();
        const foundYear = dataYears.value.find(el => new Date(el.d).getUTCFullYear() === year);
        if(!foundYear){
            dataYears.value.push({
                d: entry.d,
                data: [ entry.v || 0.00 ]
            })
        } else {
            foundYear.data.push(entry.v)
        }
    });
    formattedChartData.value = rawData
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

.monthly-flow-container {
    height: 100%;

    #monthly-flow-chart-container {
        height: 100%;

        .svg-wrap-mf {
            height: 100%;

            .d3-chart-mf {
                height: 100%;
            }
        }
    }
}
</style>
