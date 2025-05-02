<template>
    <div class="text-h4">Flow Duration Tool</div>
    <div class="flow-duration-container">
        <div class="col">
            <div class="row">
                <FlowDuration />
            </div>
            <div class="row">
                <TotalRunoff />
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
import FlowDuration from '@/components/streamflow/FlowDuration.vue';

</script>

<style lang="scss">
.flow-duration-container {
    display: flex;
}
</style>
