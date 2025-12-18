<template>
    <div class="report-break watershed-summary">
        <div class="spaced-flex-row report-header">
            <div>
                <div class="text-h4 q-my-lg">Watershed Summary</div>
                <div class="text-h5">{{ props.reportContent.overview.watershedName }} (WFI: {{ props.wfi }})</div>
                <div class="text-h6">{{ new dayjs().format('MMMM DD, YYYY') }}</div>
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
        <div class="summary-map-container">
            <img 
                class="summary-map"
                :src="props.reportContent.overview.watershedImg" alt="Watershed Map Image" 
            />
        </div>
        <hr class="q-my-xl" data-html2canvas-ignore="true" />
    </div>
</template>
<script setup>
import dayjs from 'dayjs';

const props = defineProps({
    reportContent: {
        type: Object,
        default: () => {},
        required: true,
    },
    wfi: {
        type: String,
        default: '',
    }
});

</script>

<style lang="scss">
.watershed-summary {
    .summary-map-container {
        display: flex;
        justify-content: center;
        align-items: center;

        .summary-map {
            // display png only on report
            height: 50rem;
            visibility: none;
            height: 0;
            width: 40rem;
            margin: 0 5rem;
        }
    }
}
</style>
