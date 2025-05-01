<template>
    <div>
        <div class="spaced-flex-row">
            <div>
                <h1>Watershed Summary</h1>
                <h2>{{ props.reportContent.overview.watershedName }}</h2>
            </div>
            <div class="location-timeline">
                <div :style="cssVars" class="bus-stops">
                    <div class="stops">
                        <div
                            v-for="(item, index) in busStops"
                            :key="index"
                            :class="[item ? 'circle' : 'line']"
                        />
                    </div>
                    <div class="labels">
                        <div
                            v-for="(item, index) in props.reportContent.overview
                                .busStopNames"
                            :key="index"
                            class="label-container"
                        >
                            <div class="label">
                                {{ item }}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <hr />
        <h1 class="q-my-lg">Overview</h1>
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
            <p>
                {{ props.reportContent.overview.max_elev }} m (max),
                {{ props.reportContent.overview.avg_elev }} m (mean),
                {{ props.reportContent.overview.min_elev }} m (min),
            </p>
        </div>
        <div class="overview-line">
            <p>Mean Annual Discharge</p>
            <p>
                {{ props.reportContent.overview.mad_m3s.toFixed(3) }}
                m<sup>3</sup>/s
            </p>
        </div>

        <div class="overview-paragraph">
            <p>
                <b
                    >Estimates of water supply represent long-term average
                    conditions.</b
                >
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
        <hr />
    </div>
</template>

<script setup>
import { computed } from "vue";
const props = defineProps({
    reportContent: {
        type: Object,
        default: () => {},
    },
});

const busStops = computed(() => {
    const myStops = [];
    props.reportContent.overview.busStopNames.forEach((element, index) => {
        myStops.push(element);
        if (index !== props.reportContent.overview.busStopNames.length - 1) {
            myStops.push(null);
        }
    });
    return myStops;
});

const cssVars = computed(() => {
    let rowHeight = 12;
    if (props.reportContent.overview.busStopNames.length < 4) {
        rowHeight = 20;
    } else if (props.reportContent.overview.busStopNames.length < 7) {
        rowHeight = 16;
    }
    return {
        "--row-height": `${rowHeight}px`,
        "--first-row-height": `${rowHeight + 2}px`,
    };
});
</script>

<style lang="scss">
.bus-stops {
    display: flex;
    flex-direction: row;
    align-content: center;

    .stops {
        flex: 0 0 1em;
        margin-right: 0.5em;
        padding: 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: space-between;

        .circle {
            height: var(--row-height);
            width: var(--row-height);
            border: 0.2em $color-stops solid;
            border-radius: 50%;
            box-sizing: border-box;
            display: inline-block;

            &:first-child {
                height: var(--first-row-height);
                width: var(--first-row-height);
                border-color: $color-first-stop;
            }
        }

        .line {
            flex: 1;
            width: 0.3em;
            background-color: $color-stops;
            display: inline-block;
            margin: -1px 0;
        }
    }

    .labels {
        flex: 1;
        display: flex;
        flex-direction: column;
        justify-content: space-between;

        .label-container {
            height: var(--row-height);
            display: flex;
            flex-direction: column;
            justify-content: center;

            .label {
                line-height: var(--row-height);
                color: $color-labels;
                font-size: var(--row-height);
                font-weight: 400;
                white-space: nowrap;
            }

            &:first-child {
                .label {
                    font-weight: 700;
                    font-size: var(--first-row-height);
                }
            }
        }
    }
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
