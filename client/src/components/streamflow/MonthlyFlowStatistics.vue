<template>
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
            class="flow-duration-tooltip"
            :style="`left: ${tooltipPosition[0]}px; top: ${tooltipPosition[1]}px`"
        >
            <q-card>
                <div 
                    v-for="(key, idx) in Object.keys(tooltipData)"
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
                        :class="['Max', 'Median', 'Min'].includes(key) ? 'val' : 'box-val'"
                    >
                        {{ key }}: {{ tooltipData[key].toFixed(2) }}
                    </div>
                </div>
            </q-card>
        </div>
    </div>
</template>

<script setup>
import * as d3 from "d3";
import { monthAbbrList } from '@/utils/dateHelpers.js';
import { onMounted, ref, watch } from 'vue';

const props = defineProps({
    startEndYears: {
        type: Array,
        default: () => [],
    },
    data: {
        type: Array,
        default: () => [],
    }
})

const monthDataArr = ref([]);
const loading = ref(false);
const monthPercentiles = ref([]);

// chart variables
const svgWrap = ref();
const svgEl = ref();
const svg = ref();
const g = ref();
const xScale = ref();
const yScale = ref();
const yMax = ref();
const yMin = ref();

// brush functionality
const brushVar = ref();
const brushEl = ref();
const brushedStart = ref();
const brushedEnd = ref();

// chart constants
const width = 600;
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

watch(() => props.startEndYears, (newval) => {
    loading.value = true;
    processData(props.data)
    addBoxPlots();
    loading.value = false;
});

onMounted(() => {
    loading.value = true;
    initializeChart();
    loading.value = false;
});

const initializeChart  = () => {
    if (svg.value) {
        d3.selectAll('.g-els.mf').remove();
    }

    processData(props.data);
    svgWrap.value = document.querySelector('.svg-wrap-mf');
    svgEl.value = svgWrap.value.querySelector('svg');
    svg.value = d3.select(svgEl.value)
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .attr("transform", `translate(${margin.left}, ${margin.top})`);
        
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

const mouseMoved = (event) => {
    const [gX, gY] = d3.pointer(event, svg.value.node());
    if (gX < margin.left || gX > width + margin.right) return;
    if (gY > height + margin.top) return;
    const date = scaleBandInvert(xScale.value)(gX - xScale.value.bandwidth());
    const foundData = monthPercentiles.value.find(el => el.month === date);

    // some custom handling for the tooltip content, depending on their values
    tooltipData.value = {};
    tooltipData.value.Month = foundData.month
    tooltipData.value.Max = foundData.max
    tooltipData.value['75th %ile'] = foundData.p75
    tooltipData.value.Median = foundData.p50
    tooltipData.value['25th %ile'] = foundData.p25
    tooltipData.value.Min = foundData.min
    tooltipPosition.value = [event.pageX - 280, event.pageY - 100];
    showTooltip.value = true;
}

const addBoxPlots = (scale = { x: xScale.value, y: yScale.value }) => {
    d3.selectAll('.mf-boxplot').remove();

    monthPercentiles.value.forEach(month => {
        // add maximum lines
        g.value
            .append('line')
            .style('stroke', 'black')
            .style('stroke-width', 2)
            .attr('class', 'mf-boxplot')
            .attr('x1', scale.x(month.month))
            .attr('y1', scale.y(month.max))
            .attr('x2', scale.x(month.month) + scale.x.bandwidth())
            .attr('y2', scale.y(month.max))

        // add max to top of box line
        g.value
            .append('line')
            .style('stroke', 'black')
            .style("stroke-dasharray", "10, 3")
            .style('stroke-width', 2)
            .attr('class', 'mf-boxplot')
            .attr('x1', scale.x(month.month) + scale.x.bandwidth() / 2)
            .attr('y1', scale.y(month.max))
            .attr('x2', scale.x(month.month) + scale.x.bandwidth() / 2)
            .attr('y2', scale.y(month.p75))

        // add box
        g.value
            .append('rect')
            .attr('class', 'mf-boxplot')
            .attr('x', scale.x(month.month))
            .attr('y', scale.y(month.p75))
            .attr('width', scale.x.bandwidth())
            .attr('height', scale.y(month.p25) - scale.y(month.p75))
            .attr('stroke', 'black')
            .attr('fill', 'steelblue');
        
        // add median lines
        g.value
            .append('line')
            .style('stroke', 'black')
            .style('stroke-width', 2)
            .attr('class', 'mf-boxplot')
            .attr('x1', scale.x(month.month))
            .attr('y1', scale.y(month.p50))
            .attr('x2', scale.x(month.month) + scale.x.bandwidth())
            .attr('y2', scale.y(month.p50))

        // add min to bottom of box line
        g.value
            .append('line')
            .style('stroke', 'black')
            .style("stroke-dasharray", "10, 3")
            .style('stroke-width', 2)
            .attr('class', 'mf-boxplot')
            .attr('x1', scale.x(month.month) + scale.x.bandwidth() / 2)
            .attr('y1', scale.y(month.p25))
            .attr('x2', scale.x(month.month) + scale.x.bandwidth() / 2)
            .attr('y2', scale.y(month.min))
            
        // add minimum lines
        g.value
            .append('line')
            .style('stroke', 'black')
            .style('stroke-width', 2)
            .attr('class', 'mf-boxplot')
            .attr('x1', scale.x(month.month))
            .attr('y1', scale.y(month.min))
            .attr('x2', scale.x(month.month) + scale.x.bandwidth())
            .attr('y2', scale.y(month.min))
            .attr('transform', `translate(0, 0)`)
    })
}

const scaleBandInvert = (scale) => {
    let domain = scale.domain();
    var paddingOuter = scale(domain[0]);
    var eachBand = scale.step();
    return (val) => {
        var index = Math.floor((val - paddingOuter) / eachBand);
        return domain[Math.max(0, Math.min(index, domain.length - 1))];
    };
};

const addBrush = () => {
    brushVar.value = d3.brushX()
        .extent([[0, 0], [width, height]])
        .on("end", brushEnded)
    
    brushEl.value = svg.value.append("g")
        .call(brushVar.value)
        .attr('transform', `translate(${margin.left}, ${margin.top})`)
}

const brushEnded = (event) => {
    const selection = event.selection;
    if (!event.sourceEvent || !selection) {
        if(selection === null){
            emit('range-selected', monthAbbrList[0], monthAbbrList[monthAbbrList.length - 1]);
        }
        return;
    };
    const [x0, x1] = selection.map(d => {
        return scaleBandInvert(xScale.value)(d)
    });

    brushedStart.value = x0;
    brushedEnd.value = x1;

    emit('range-selected', brushedStart.value, brushedEnd.value);
    
    brushEl.value
        .transition()
        .call(
            brushVar.value.move, 
            [xScale.value(x0), xScale.value(x1) + xScale.value.bandwidth()]
        );
}

const addAxes = (scale = { x: xScale.value, y: yScale.value }) => {
    d3.selectAll('.mf.axis').remove();
    d3.selectAll('.mf.axis-label').remove();
    // x axis labels and lower axis line
    g.value.append('g')
        .attr('class', 'x axis mf')
        .call(d3.axisBottom(scale.x))
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

const setAxes = () => {
    // set x-axis scale
    xScale.value = d3.scaleBand()
        .domain(monthAbbrList)
        .range([0, width])
        .padding(0.2)

    // set y-axis scale
    const valsToCheck = monthPercentiles.value.map(d => d);

    yMax.value = d3.max(valsToCheck.map(el => el.max));
    yMax.value *= 1.10;
    yMin.value = 0;

    // Y axis
    yScale.value = d3.scaleSymlog()
        .range([height, 0])
        .domain([0, yMax.value]);
}

const processData = (data) => {
    const dataToProcess = data.filter(el => {
        return (new Date(el.d).getUTCFullYear() >= props.startEndYears[0]) && (new Date(el.d).getUTCFullYear() <= props.startEndYears[1])
    });

    // sort data into month groups
    sortDataIntoMonths(dataToProcess);

    monthPercentiles.value = [];
    monthDataArr.value.forEach(month => {
        monthPercentiles.value.push({
            month: monthAbbrList[month.month],
            max: percentile(month.data.filter(el => el.v !== null), 100),
            p75: percentile(month.data.filter(el => el.v !== null), 75),
            p50: percentile(month.data.filter(el => el.v !== null), 50),
            p25: percentile(month.data.filter(el => el.v !== null), 25),
            min: percentile(month.data.filter(el => el.v !== null), 0)
        })
    })
}

const sortDataIntoMonths = (data) => {
    monthAbbrList.forEach((_, idx) => {
        const foundMonth = monthDataArr.value.find(el => el.month === idx);
        const currMonthData = data.filter(el => {
            return new Date(el.d).getMonth() === idx;
        });
        if(!foundMonth){
            monthDataArr.value.push({
                month: idx,
                data: currMonthData
            })
        } else {
            foundMonth.data = currMonthData
        }
    })

    monthDataArr.value.forEach(month => {
        month.data.sort((a, b) => {
            return a.v - b.v
        });
    });
}

const percentile = (sortedArray, p) => {
    if(sortedArray.length > 0){
        const index = (p / 100) * (sortedArray.length - 1);
        const lower = Math.floor(index);
        const upper = Math.ceil(index);

        if (lower === upper) {
            return sortedArray[lower].v;
        }

        const weight = index - lower;

        return sortedArray[lower].v * (1 - weight) + sortedArray[upper].v * weight;
    } else {
        return 0;
    }
} 

</script>

<style lang="scss">

// elements clipped by the clip-path rectangle
.flow-duration-clipped {
    clip-path: url('#flow-duration-box-clip');
} 

.flow-duration-container {
    position: relative;
    display: flex;

    .flow-duration-tooltip {
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
}
</style>
