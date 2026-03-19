<template>
    <report-section
        :id="id"
        title=""
        class="is-hidden-touch static-allocations-table-section"
    >
        <div v-if="reportContent.allocations.length !== 0">
            <pdf-allocations-wrapper
                v-for="(allocationType, index) in allocationTypes"
                :key="index"
                :intro-data="{
                    totalAllocationVolume,
                    licenceCount,
                    licencePluralization,
                }"
                :licences="reportContent.allocations"
                :selected-type="allocationType"
                :index="index"
            />
        </div>

        <h4
            v-else
            class="title is-4"
        >
            No Allocations for selected watershed.
        </h4>
    </report-section>
</template>

<script setup>
import ReportSection from '@/components/watershed/report/ReportSection.vue'
import PdfAllocationsWrapper from '@/components/watershed/report/PdfAllocationsWrapper.vue';
import { computed, ref } from 'vue';

const props = defineProps({
    reportContent: {
        type: Object,
        default: () => {}
    }
});

// declared statically so order will always be the same across reports
const allocationTypes = ref([
    'sw-lic',
    'gw-lic',
    'sw-stu',
    'gw-stu',
    'sw-app',
    'gw-app',
]);

const totalAllocationVolume = computed(() => {
    return props.reportContent.overview.annualSurfaceWaterAllocation
        + props.reportContent.overview.annualGroundwaterAllocation;
})
const licenceCount = computed(() => {
    const uniqueLicenceNumbers = new Set(props.reportContent.allocations.map(allocation => allocation.licence_no));
    return uniqueLicenceNumbers.size;
});
const licencePluralization = computed(() => {
    if (props.reportContent.allocations.length === 1) {
        return 'Licence';
    }
    return 'Licences';
});
</script>

<style lang="scss">
</style>
