<template>
    <div class="text-h4">Flow Duration Tool</div>
    <div class="flow-duration-container">
        <div class="col">
            <div class="row">
                <FlowDuration 
                    :data="data"
                    @range-selected="onRangeSelected"
                />
            </div>
            <div class="row">
                <TotalRunoff 
                    :data="data"
                    :start-end-range="[monthRangeStart, monthRangeEnd]"
                />
            </div>
        </div>
        <div class="col">
            <MonthlyFlowStatistics />
        </div>
    </div>
</template>

<script setup>
import MonthlyFlowStatistics from '@/components/streamflow/MonthlyFlowStatistics.vue';
import TotalRunoff from '@/components/streamflow/TotalRunoff.vue';
import flowDuration from '@/constants/flowDuration.json';
import FlowDuration from '@/components/streamflow/FlowDuration.vue';
import { onMounted, ref } from 'vue';

const data = ref([]);
const monthRangeStart = ref('Jan');
const monthRangeEnd = ref('Dec');

onMounted(() => {
    getFlowDurationData();
});

const onRangeSelected = (start, end) => {
    monthRangeStart.value = start;
    monthRangeEnd.value = end;
}

/**
 * retrieves the data for the flow duration charts
 */
const getFlowDurationData = () => {   
    data.value = flowDuration;
}

</script>

<style lang="scss">
.flow-duration-container {
    display: flex;
}
</style>
4
