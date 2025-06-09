<template>
    <div class="text-h4">Flow Duration Tool</div>
    <div 
        v-if="props.chartData"
        class="flow-duration-container"
    >
        <div class="col">
            <div class="row">
                <MonthlyFlowStatistics
                    :chart-data="props.chartData.monthlyFlowStatistics"
                    :start-end-years="[yearRangeStart, yearRangeEnd]"
                    :start-end-months="[monthRangeStart, monthRangeEnd]"
                    @range-selected="onRangeSelected"
                />
            </div>
            <div class="row">
                <FlowDuration 
                    :data="props.chartData.flowDuration"
                    :start-end-years="[yearRangeStart, yearRangeEnd]"
                    :start-end-months="[monthRangeStart, monthRangeEnd]"
                />
            </div>
        </div>
        <div class="col">
            <!-- <TotalRunoff
                :data="props.chartData"
                :start-end-months="[monthRangeStart, monthRangeEnd]" 
                @month-selected="(start, end) => onRangeSelected(start, end)"
                @year-range-selected="onYearRangeSelected"
            /> -->
        </div>
    </div>
</template>

<script setup>
import MonthlyFlowStatistics from '@/components/streamflow/MonthlyFlowStatistics.vue';
import TotalRunoff from '@/components/streamflow/TotalRunoff.vue';
import FlowDuration from '@/components/streamflow/FlowDuration.vue';
import { onMounted, ref } from 'vue';

const monthRangeStart = ref('Jan');
const monthRangeEnd = ref('Dec');
const yearRangeStart = ref(0);
const yearRangeEnd = ref(3000);

const props = defineProps({
    chartData: {
        type: Object,
        default: () => {}
    }
});

onMounted(async () => {
    yearRangeStart.value = props.chartData.monthlyFlowStatistics[0].year;
    yearRangeEnd.value = props.chartData.monthlyFlowStatistics[props.chartData.monthlyFlowStatistics.length - 1];
});

const onRangeSelected = (start, end) => {
    monthRangeStart.value = start;
    monthRangeEnd.value = end;
}

const onYearRangeSelected = (start, end) => {
    yearRangeStart.value = start;
    yearRangeEnd.value = end;
}

</script>

<style lang="scss">
.flow-duration-container {
    display: flex;
}
</style>
