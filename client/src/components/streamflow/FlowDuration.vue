<template>
    <h3>Flow Duration</h3>
    <div id="flow-duration-chart-container">
        <div class="svg-wrap">
                <svg class="d3-chart">
                    <!-- d3 chart content renders here -->
                </svg>
            </div>
    </div>
</template>

<script setup>
import * as d3 from "d3";
import flowDuration from '@/constants/flowDuration.json';
import { monthAbbrList } from '@/constants/dateHelpers.js';
import { onMounted, ref } from 'vue';

const monthDataArr = ref([]);
const loading = ref(false);

// chart variables
const svgWrap = ref();
const svgEl = ref();
const svg = ref();
const width = 800;
const height = 500;

onMounted(() => {
    loading.value = true;
    processData(flowDuration);
    initializeChart();
    loading.value = false;
});

const initializeChart  = () => {
    svg.value = '';
}

const processData = (data) => {
    // sort data into month groups
    sortDataIntoMonths(data);
    const monthPercentiles = [];
    monthDataArr.value.forEach(month => {
        monthPercentiles.push({
            month: month.month,
            max: percentile(month.data.filter(el => el.v !== null), 100),
            p75: percentile(month.data.filter(el => el.v !== null), 75),
            p50: percentile(month.data.filter(el => el.v !== null), 50),
            p25: percentile(month.data.filter(el => el.v !== null), 25),
            min: percentile(month.data.filter(el => el.v !== null), 0)
        })
    })

    console.log(monthPercentiles)
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

const calculateExceedance = (sortedDescendingArray) => {
    const N = sortedDescendingArray.length;
    return sortedDescendingArray.map((value, i) => {
        return {
            value,
            exceedance: ((i + 1) / N) * 100
        }
    });
}

const percentile = (sortedArray, p) => {
    const index = (p / 100) * (sortedArray.length - 1);
    const lower = Math.floor(index);
    const upper = Math.ceil(index);

    if (lower === upper) {
        return sortedArray[lower].v;
    }

    const weight = index - lower;

    return sortedArray[lower].v * (1 - weight) + sortedArray[upper].v * weight;
} 

</script>
