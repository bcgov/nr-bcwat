<template>
    <div class="text-h4">Flow Duration Tool</div>
    <div 
        v-if="props.chartData"
        class="flow-duration-container"
    >
        <div class="col">
            <div class="row">
                <MonthlyFlowStatistics
                    :chart-data="monthlyFlowStatisticsData"
                    :start-end-years="[yearRangeStart, yearRangeEnd]"
                    :start-end-months="[monthRangeStart, monthRangeEnd]"
                    @range-selected="onRangeSelected"
                />
            </div>
            <div class="row">
                <FlowDuration 
                    :data="flowDurationData"
                    :start-end-years="[yearRangeStart, yearRangeEnd]"
                    :start-end-months="[monthRangeStart, monthRangeEnd]"
                />
            </div>
        </div>
        <div class="col">
            <TotalRunoff
                :data="totalRunoffData"
                :start-end-months="[monthRangeStart, monthRangeEnd]" 
                @month-selected="(start, end) => onRangeSelected(start, end)"
                @year-range-selected="onYearRangeSelected"
            />
        </div>
    </div>
</template>

<script setup>
import MonthlyFlowStatistics from '@/components/streamflow/MonthlyFlowStatistics.vue';
import TotalRunoff from '@/components/streamflow/TotalRunoff.vue';
import FlowDuration from '@/components/streamflow/FlowDuration.vue';
import { monthAbbrList } from "@/utils/dateHelpers.js";
import { getFlowDurationByIdAndDateRange } from '@/utils/api.js';
import { computed, onMounted, ref } from 'vue';

const monthRangeStart = ref('Jan');
const monthRangeEnd = ref('Dec');
const yearRangeStart = ref(0);
const yearRangeEnd = ref(3000);
const fetchedData = ref();

const props = defineProps({
    chartData: {
        type: Object,
        default: () => {}
    },
    id: {
        type: Number,
        default: -1
    }
});

onMounted(async () => {
    yearRangeStart.value = props.chartData.monthlyFlowStatistics[0].year;
    yearRangeEnd.value = props.chartData.monthlyFlowStatistics[props.chartData.monthlyFlowStatistics.length - 1];
});

const monthlyFlowStatisticsData = computed(() => {
    if(fetchedData.value){
        return fetchedData.value.flowDuration.monthlyFlowStatistics;
    }
    return props.chartData.monthlyFlowStatistics;
});

const flowDurationData = computed(() => {
    if(fetchedData.value){
        return fetchedData.value.flowDuration.flowDuration;
    }
    return props.chartData.flowDuration;
});

const totalRunoffData = computed(() => {
    if(fetchedData.value){

        return fetchedData.value.flowDuration.totalRunoff;
    }
    return props.chartData.totalRunoff
})

const onRangeSelected = (start, end) => {
    monthRangeStart.value = start;
    monthRangeEnd.value = end;
}

const onYearRangeSelected = async (start, end) => {
    yearRangeStart.value = start;
    yearRangeEnd.value = end;
    fetchedData.value = await getFlowDurationByIdAndDateRange(props.id, start, end, (monthAbbrList.findIndex(month => month === monthRangeStart.value) + 1));
}

</script>

<style lang="scss">
.flow-duration-container {
    display: flex;
}
</style>
