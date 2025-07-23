
<template>
    <h3>Flow Duration (range here)</h3>
    <div id="total-runoff-chart-container">
        <div class="svg-wrap-fd">
            <svg class="d3-chart-fd">
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
            <div class="tooltip-header text-h6">
                {{ tooltipData.exceedance }}% Exceedance Flow
            </div>
            <div class="tooltip-row">
                {{ tooltipData.flow }} (m³/s)
            </div>
        </q-card>
    </div>
</template>

<script setup>
import * as d3 from "d3";
import { sciNotationConverter } from '@/utils/chartHelpers.js';
import { monthAbbrList } from '@/utils/dateHelpers.js';
import { onMounted, ref, watch } from "vue";

const props = defineProps({
    data: {
        type: Array,
        default: () => [],
    },
});

const formattedChartData = ref([]);

// chart variables
const svgEl = ref();
const svg = ref();
const g = ref();
const yMax = ref(0);
const flowLine = ref();
const hoverCircle = ref();
const transition = ref();
const axisLeft = ref();

// chart scaling
const xScale = ref();
const yScale = ref();

// chart constants 
const width = 600;
const height = 300;
const margin = {
    left: 50,
    right: 50,
    top: 20,
    bottom: 50
};

// tooltip
const showTooltip = ref(false);
const tooltipData = ref();
const tooltipPosition = ref();

onMounted(() => {
    initializeSvg();
});

/**
 * Chart set up and rendering each component in the desired order. 
 */
const initializeSvg = () => {
    if (svg.value) {
        d3.selectAll('.g-els.fd').remove();
    }

    svgEl.value = document.querySelector('.svg-wrap-fd > svg');
    svg.value = d3.select(svgEl.value)
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .attr("transform", `translate(${margin.left}, ${margin.top})`);

    g.value = svg.value.append('g')
        .attr('class', 'g-els fd')
        .attr("transform", `translate(${margin.left}, ${margin.top})`);

    // add clip-path element - removing content outside the chart
    const defs = g.value.append('defs');
    defs.append('clipPath')
        .attr('id', 'total-runoff-box-clip')
        .append('rect')
        .attr('width', width)
        .attr('height', height);

    setAxes();
    addAxes();
    addFlowLine();

    svg.value.on('mousemove', mouseMoved);
    svg.value.on('mouseout', mouseOut);
};

const mouseOut = () => {
    showTooltip.value = false;
}

/**
 * handler for mouse movement on the chart. This is responsible for setting the tooltip 
 * content via inverting the scale for a given mouse position. 
 * 
 * @param event mouseMove event
 */
const mouseMoved = (event) => {
    if(hoverCircle.value) g.value.selectAll('.dot').remove();
    const [gX, gY] = d3.pointer(event, svg.value.node());
    if (gX < margin.left || gX > width) return;
    if (gY > height + margin.top || gY <= 20) return;
    const percentile = xScale.value.invert(gX);
    const bisect = d3.bisector(d => d.exceedance).center;
    const idx = bisect(props.data, percentile - 10);
    const data = props.data[idx];

    if(!formattedChartData.value[idx]) return;
    addHoverCircle(idx);
    
    tooltipData.value = {
        exceedance: data.exceedance ? data.exceedance.toFixed(2) : 0.00,
        flow: data.value
    };
    tooltipPosition.value = [event.pageX - 280, event.pageY - 20];
    showTooltip.value = true;
};

/**
 * Appends a small circle to the chart to provide a simple way to see where the user
 * is hovering. 
 * 
 * @param index - the index of the dataset to reference to set both the x and y axis positions
 */
const addHoverCircle = (index) => {
    if(!formattedChartData.value[index]) return;
    hoverCircle.value = g.value.append('circle')
        .attr('class', 'dot')
        .attr("r", 4)
        .attr('cy', yScale.value(formattedChartData.value[index].value))
        .attr('cx', xScale.value(formattedChartData.value[index].exceedance))
        .attr('fill', 'steelblue')
};

/**
 * Renders the flow line path onto the chart area. 
 */
const addFlowLine = () => {
    d3.selectAll('.fd.line').remove();

    flowLine.value = g.value.append('path')
        .datum(formattedChartData.value)
        .attr('fill', 'none')
        .attr('stroke', 'steelblue')
        .attr('stroke-width', 2)
        .attr('class', 'fd line streamflow-clipped')
        .attr('d', d3.line()
            .x(d => xScale.value(0))
            .y(d => yScale.value(0))
        )
        
    flowLine.value
        .transition()
        .duration(500)
        .attr('stroke', 'steelblue')
        .attr('stroke-width', 2)
        .attr('class', 'fd line streamflow-clipped')
        .attr('d', d3.line()
            .x(d => {
                return xScale.value(d.exceedance)
            })
            .y(d => {
                return yScale.value(d.value)
            })
        )
        .attr('transform', 'translate(1, 0)')
}


/**
 * Renders x and y axes onto the chart area. 
 */
const addAxes = () => {
     // bottom axis
    g.value.append('g')
        .attr('class', 'axis axis--x')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(xScale.value).tickFormat(d3.format('.0%')));

    // left axis
    axisLeft.value = d3.axisLeft(yScale.value)
        .ticks(3)
        .tickFormat(sciNotationConverter);

    g.value.append('g')
        .attr('class', 'axis axis--y')
        .attr('transform', 'translate(-2,0)');
}

/**
 * Setup function for the x and y axis. Maximum value is arbitrarily set to 10% higher
 * than the actual maximum of the data to provide some padding around the top 
 * of the chart
 */
const setAxes = () => {
    // set x-axis scale
    xScale.value = d3.scaleLinear()
        .domain([-10, 110])
        .range([0, width])

    // set y-axis scale
    yMax.value = d3.max(formattedChartData.value.map(el => el.value));
    yMax.value *= 1.10;

    // Y axis
    yScale.value = d3.scaleSymlog()
        .range([height, 0])
        .domain([0, yMax.value]);

    transition.value = d3.transition().duration(500);
}

/**
 * handles the provided data and calculates the exceedance for the currently
 * selected range of data. 
 * 
 * @param dataToProcess - Array of all of the data returned by the API
 * @param range - start and end month array. eg. ['Jan', 'Dec']
 */
const processData = (dataToProcess, monthRange, yearRange) => {
    const startMonth = monthAbbrList.indexOf(monthRange[0])
    const endMonth = monthAbbrList.indexOf(monthRange[1])
    const dataInRange = dataToProcess.filter(el => {
        const monthIdx = new Date(el.d).getUTCMonth();
        const year = new Date(el.d).getUTCFullYear();
        if(yearRange){
            return (monthIdx >= startMonth && monthIdx <= endMonth) && (year >= yearRange[0] && year <= yearRange[1]);
        } else {
            return (monthIdx >= startMonth && monthIdx <= endMonth);
        };
    })
    formattedChartData.value = calculateExceedance(dataInRange.sort((a, b) => b.v - a.v))
}
const calculateExceedance = (sortedDescendingArray) => {
    const N = sortedDescendingArray.length;
    return sortedDescendingArray.map((value, i) => {
        return {
            value: value.v,
            exceedance: ((i + 1) / N) * 100
        }
    });
}
</script>

<style lang="scss">
// elements clipped by the clip-path rectangle
.total-runoff-clipped {
    clip-path: url('#total-runoff-box-clip');
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
            color: white;
            background-color: steelblue;
        }
    }
</style>
