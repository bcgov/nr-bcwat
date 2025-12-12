<template>
    <div class="report-break watershed-summary">
        <div class="spaced-flex-row report-header">
            <div>
                <div class="text-h4 q-my-lg">Watershed Summary</div>
                <div class="text-h5">{{ props.reportContent.overview.watershedName }} (WFI: {{ props.wfi }})</div>
            </div>
            <div class="location-timeline">
                <q-timeline>
                    <q-timeline-entry
                        v-for="(item, index) in props.reportContent.overview.busStopNames"
                        :key="index"
                        :title="item"
                        :color="index === 0 ? 'orange' : ''"
                        layout="dense"
                        side="right"
                    />
                </q-timeline>
            </div>
        </div>
        <div>
            <img 
                class="summary-map"
                :src="props.reportContent.overview.watershedImg" alt="Watershed Map Image" 
            />
        </div>
        <hr class="q-my-xl"/>
    </div>
</template>
<script setup>
const props = defineProps({
    reportContent: {
        type: Object,
        default: () => {},
    },
    points: {
        type: Object,
        default: () => {},
    },
    wfi: {
        type: String,
        default: '',
    }
});

</script>

<style lang="scss">
.watershed-summary {
    .summary-map {
        // display png only on report
        // height: 50rem;
        visibility: none;
        height: 0; 
        margin: auto;
    }
}
</style>
