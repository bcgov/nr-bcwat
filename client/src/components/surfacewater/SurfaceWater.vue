<template>
    <div>
        <div class="page-container">
            <MapFilters
                title="Water Allocations"
                :loading="pointsLoading"
                :points-to-show="features"
                :active-point-id="activePoint?.id"
                :total-point-count="points.features.length"
                :filters="streamflowFilters"
                @update-filter="(newFilters) => updateFilters(newFilters)"
                @select-point="(point) => selectPoint(point)"
                @view-more="reportOpen = true"
            />
            <Map @loaded="(map) => loadPoints(map)" />
        </div>
        <SurfaceWaterQualityReport
            :active-point="activePoint"
            :report-open="reportOpen"
            @close="reportOpen = false"
        />
    </div>
</template>

<script setup>
import Map from "@/components/Map.vue";
import MapFilters from '@/components/MapFilters.vue';
import SurfaceWaterQualityReport from "@/components/surfacewater/SurfaceWaterQualityReport.vue";
</script>

<!-- Cannot leave style tag out without breaking map for some reason -->
<style lang="scss" scoped>
.map {
    height: auto;
}

.streamflow-details {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 10 !important;
    background-color: grey;
}
</style>
