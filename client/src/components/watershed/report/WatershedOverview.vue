<template>
    <div>
        <div class="report-break">
            <div class="spaced-flex-row">
                <div>
                    <div class="text-h4">Watershed Summary</div>
                    <div class="text-h4">{{ props.reportContent.overview.watershedName }}</div>
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
            <q-separator />
            <div :class="props.isReport ? 'report-section-header' : ''">
                <div class="text-h4 q-my-lg">Overview</div>
            </div>
            <div class="overview-line">
                <p>Coordinates:</p>
                <p>
                    {{ props.reportContent.overview.mgmt_lat.toFixed(3) }}° N,
                    {{ props.reportContent.overview.mgmt_lng.toFixed(3) }}° W
                </p>
            </div>
            <div class="overview-line">
                <p>Watershed Area:</p>
                <p>
                    {{ props.reportContent.overview.area_km2.toFixed(2) }} km<sup
                        >2</sup
                    >
                </p>
            </div>
            <div class="overview-line">
                <p>Watershed Elevation:</p>
                <p v-if="props.reportContent.overview.max_elev && props.reportContent.overview.avg_elev && props.reportContent.overview.min_elev">
                    {{ props.reportContent.overview.max_elev }} m (max),
                    {{ props.reportContent.overview.avg_elev }} m (mean),
                    {{ props.reportContent.overview.min_elev }} m (min),
                </p>
                <p v-else>
                    Not Available
                </p>
            </div>
            <div class="overview-line">
                <p>Mean Annual Discharge</p>
                <p>
                    {{ props.reportContent.overview.mad_m3s.toFixed(3) }}
                    m³/s
                </p>
            </div>

            <div class="overview-paragraph">
                <p>
                    <b>Estimates of water supply represent long-term average conditions.</b>
                    These estimates were generated from hydrology models. The models
                    incorporate information about climate, terrain, land cover,
                    evapotranspiration, watershed boundaries and connectivity, and
                    observed hydrology, and are calibrated using long-term
                    streamflow monitoring data collected by the Water Survey of
                    Canada, United States Geological Survey, and other
                    organizations. Detailed information on models and performance is
                    provided in the methods section of this report. Environmental
                    flow needs calculations identify the amount of water rivers
                    require to maintain healthy aquatic ecosystems. The calculations
                    presented in this report are based on the Province of BC's
                    Environmental Flow Needs Policy.
                </p>
                <p>
                    <b
                        >Water allocations represent existing water rights and are
                        sourced directly from government databases.</b
                    >
                    These allocations include both short-term (temporary diversion)
                    and long-term licences at the time of licence extract as noted
                    within the report. Volumes of water indicated as consumptive use
                    associated with these allocations are summarized and integrated
                    with the estimates of water supply to provide a complete picture
                    of the resource. Licences for all purposes are included. Both
                    surface water and groundwater allocations within the watershed
                    have been summarized. In some cases, assumptions have been made
                    around timing of use (e.g. agriculture) where that information
                    is not explicitly supplied with the source data. Information on
                    all licences are included in this report along with notes
                    indicating any assumptions made.
                </p>
            </div>
        </div>
        <q-separator v-if="!props.isReport" class="q-my-xl" />
    </div>
</template>

<script setup>
import { onMounted } from "vue";
const props = defineProps({
    reportContent: {
        type: Object,
        default: () => {},
    },
    isReport: {
        type: Boolean,
        default: false,
    }
});

onMounted(() => {
    document.overviewLoaded = true;
});
</script>

<style lang="scss">
.q-timeline__content {
    padding-bottom: 2px !important;
}

.overview-line {
    display: flex;

    p {
        padding-left: 0.5em;
        padding-right: 0.5em;
        width: 50%;
        &:first-child {
            font-weight: bold;
            text-align: end;
        }
    }
}

.overview-paragraph {
    background-color: $light-grey-accent;
    padding: 2em;
}
</style>
