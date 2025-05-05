<template>
    <div class="report-container" :class="props.reportOpen ? 'open' : ''">
        <div v-if="props.activePoint" class="report-sidebar">
            <div>
                <q-btn
                    class="q-mb-md"
                    color="white"
                    flat
                    label="Back to Map"
                    icon="reply"
                    dense
                    @click="() => emit('close')"
                />
            </div>
            <div class="text-h5 text-bold">
                Watershed {{ props.activePoint.name }}
            </div>
            <div class="text-h5 subtitle">ID: {{ props.activePoint.nid }}</div>
            <div class="header-grid">
                <div v-if="'network' in props.activePoint" class="col">
                    <div class="text-h6">Network</div>
                    <p>{{ props.activePoint.network }}</p>
                </div>
                <div v-if="'yr' in props.activePoint" class="col">
                    <div class="text-h6">Year Range</div>
                    <p>
                        {{ startYear }} -
                        {{ endYear }}
                    </p>
                </div>
                <div v-if="'status' in props.activePoint" class="col">
                    <div class="text-h6">Status</div>
                    <p>{{ props.activePoint.status }}</p>
                </div>
                <div v-if="'area' in props.activePoint" class="col">
                    <div class="text-h6">Area</div>
                    <p>{{ props.activePoint.area }} km<sup>2</sup></p>
                </div>
                <div v-if="'net' in props.activePoint" class="col">
                    <div class="text-h6">Network</div>
                    <p>{{ props.activePoint.net }}</p>
                </div>
            </div>
            <q-separator color="white" />
            <q-list class="q-mt-sm">
                <q-item
                    clickable
                    :class="viewPage === 'temperature' ? 'active' : ''"
                    @click="() => (viewPage = 'temperature')"
                >
                    <div class="text-h6">Temperature</div>
                </q-item>
                <q-item
                    clickable
                    :class="viewPage === 'precipitation' ? 'active' : ''"
                    @click="() => (viewPage = 'precipitation')"
                >
                    <div class="text-h6">Precipitation</div>
                </q-item>
                <q-item
                    clickable
                    :class="viewPage === 'snowOnGround' ? 'active' : ''"
                    @click="() => (viewPage = 'snowOnGround')"
                >
                    <div class="text-h6">Snow on Ground</div>
                </q-item>
                <q-item
                    clickable
                    :class="viewPage === 'snowWaterEquivalent' ? 'active' : ''"
                    @click="() => (viewPage = 'snowWaterEquivalent')"
                >
                    <div class="text-h6">Snow Water Equivalent</div>
                </q-item>
                <q-item
                    clickable
                    :class="viewPage === 'manualSnowSurvey' ? 'active' : ''"
                    @click="() => (viewPage = 'manualSnowSurvey')"
                >
                    <div class="text-h6">Manual Snow Survey</div>
                </q-item>
            </q-list>
            <div>
                <span class="about"
                    ><q-icon name="help" /> About this page
                    <q-tooltip>About this page content goes here.</q-tooltip>
                </span>
            </div>
            <div class="data-license cursor-pointer">Data License</div>
        </div>
        <q-tab-panels v-model="viewPage">
            <q-tab-panel name="temperature">
                <Temperature
                    :report-content="props.reportContent"
                    :start-year="startYear"
                    :end-year="endYear"
                />
            </q-tab-panel>
            <q-tab-panel name="precipitation">
                <div class="q-pa-md">
                    <Precipitation
                        :report-content="props.reportContent"
                        :start-year="startYear"
                        :end-year="endYear"
                    />
                </div>
            </q-tab-panel>
            <q-tab-panel name="snowOnGround">
                <div class="q-pa-md">Snow on Ground</div>
                <!-- <FlowMetrics /> -->
            </q-tab-panel>
            <q-tab-panel name="snowWaterEquivalent">
                <!-- <MonthlyMeanFlow /> -->
            </q-tab-panel>
            <q-tab-panel name="manualSnowSurvey">
                <!-- <StreamflowStage /> -->
            </q-tab-panel>
        </q-tab-panels>
    </div>
</template>
<script setup>
import Temperature from "@/components/climate/report/Temperature.vue";
import Precipitation from "@/components/climate/report/Precipitation.vue";
import { computed, ref } from "vue";

const emit = defineEmits(["close"]);

const props = defineProps({
    reportOpen: {
        type: Boolean,
        default: false,
    },
    reportContent: {
        type: Object,
        default: () => {},
    },
    activePoint: {
        type: Object,
        default: () => {},
    },
});

const viewPage = ref("precipitation");

const startYear = computed(() => {
    return JSON.parse(props.activePoint.yr)[0];
});
const endYear = computed(() => {
    return JSON.parse(props.activePoint.yr)[1];
});
</script>

<style lang="scss">
.q-tab-panel {
    padding: 0;
    overflow: hidden;
}
.data-license {
    display: flex;
    height: 100%;
    align-items: end;
    text-decoration: underline;
}

.about {
    cursor: pointer;
}

.q-item {
    &.active {
        background-color: $primary-light;
    }
}
</style>
