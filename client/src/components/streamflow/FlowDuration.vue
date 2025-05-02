<template>
    <h3>Flow Duration</h3>
    {{ formattedData }}
</template>

<script setup>
import * as d3 from "d3";
import flowDuration from '@/constants/flowDuration.json';
import { monthAbbrList } from '@/constants/dateHelpers.js';
import { onMounted, ref } from 'vue';

const formattedData = ref([]);
const monthDataArr = ref([]);

onMounted(() => {
    loading.value = true;
    formattedData.value = sortDataIntoMonths(flowDuration);
    loading.value = false;
})

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
        return sortedArray[lower];
    }

    const weight = index - lower;
    return sortedArray[lower] * (1 - weight) + sortedArray[upper] * weight;
} 

</script>
