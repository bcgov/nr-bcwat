<template>
    <div class="text-h4">Flow Duration Tool</div>
    <div 
        v-if="data"
        class="flow-duration-container"
    >
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
                    :start-end-months="[monthRangeStart, monthRangeEnd]"
                />
            </div>
        </div>
        <div class="col">
            <MonthlyFlowStatistics 
                :data="data"
                :start-end-months="[monthRangeStart, monthRangeEnd]" 
            />
        </div>
    </div>
</template>

<script setup>
import MonthlyFlowStatistics from '@/components/streamflow/MonthlyFlowStatistics.vue';
import TotalRunoff from '@/components/streamflow/TotalRunoff.vue';
import flowDuration from '@/constants/flowDuration.json';
import FlowDuration from '@/components/streamflow/FlowDuration.vue';
import { onMounted, ref } from 'vue';

const data = ref();
const monthRangeStart = ref('Jan');
const monthRangeEnd = ref('Dec');
const yearRangeStart = ref(1914);
const yearRangeEnd = ref(2023);

onMounted(async () => {
    await getFlowDurationData();
});

const onRangeSelected = (start, end) => {
    monthRangeStart.value = start;
    monthRangeEnd.value = end;
}

/**
 * retrieves the data for the flow duration charts
 */
const getFlowDurationData = async () => {
    data.value = flowDuration;
}

</script>

<style lang="scss">
.flow-duration-container {
    display: flex;
}
</style>
4
