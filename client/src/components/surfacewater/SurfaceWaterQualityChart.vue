<template>
    <div>
        <SurfaceWaterQualityReportChart 
            :chart-data="props.data"
            :chart-id="`surface-quality-coliform-chart-${props.data.paramId}`"
        />
    </div>
</template>

<script setup>
import SurfaceWaterQualityReportChart from '@/components/surfacewater/SurfaceWaterQualityReportChart.vue';

const props = defineProps({
    data: {
        type: Object,
        default: () => {},
    }
});
</script>

<style lang="scss">
.surface-water-quality-table {
    .header-text {
        color: grey;
    }
    th, td {
        padding: 8px;
        text-align: left;
        border-bottom: 1px solid #ddd;
    }
}

.table-cell {
    min-width: 20rem;
}
</style>
