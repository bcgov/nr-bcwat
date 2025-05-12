<template>
    <div
        class="report-container row"
        :class="props.reportOpen ? 'open' : ''"
    >
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
                    <div class="text-h6">Mean Annual Discharge</div>
                    <p>{{ props.activePoint.net }} m<sup>3</sup>/s</p>
                </div>
            </div>
            <q-separator color="white" />
            <q-list class="q-mt-sm">
                <q-item 
                    clickable 
                    :class="viewPage === 'sevenDayFlow' ? 'active' : ''"
                    @click="() => (viewPage = 'sevenDayFlow')"
                >
                    <div class="text-h6">Seven Day Flow</div>
                </q-item>
                <q-item
                    clickable
                    :class="viewPage === 'flowDurationTool' ? 'active' : ''"
                    @click="() => (viewPage = 'flowDurationTool')"
                >
                    <div class="text-h6">Flow Duration Tool</div>
                </q-item>
                <q-item 
                    clickable 
                    :class="viewPage === 'flowMetrics' ? 'active' : ''"
                    @click="() => (viewPage = 'flowMetrics')"
                >
                    <div class="text-h6">Flow Metrics</div>
                </q-item>
                <q-item 
                    clickable 
                    :class="viewPage === 'monthlyMeanFlow' ? 'active' : ''"
                    @click="() => (viewPage = 'monthlyMeanFlow')"
                >
                    <div class="text-h6">Monthly Mean Flow</div>
                </q-item>
                <q-item 
                    clickable
                    :class="viewPage === 'stage' ? 'active' : ''"
                    @click="() => (viewPage = 'stage')"
                >
                    <div class="text-h6">Stage</div>
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
            <q-tab-panel name="sevenDayFlow">
                <div class="q-ma-md full-height">
                    <SevenDayFlow 
                        v-if="props.activePoint"
                        :selected-point="props.activePoint"
                    />
                </div>
            </q-tab-panel>
            <q-tab-panel name="flowDurationTool">
                <FlowDurationTool />
            </q-tab-panel>
            <q-tab-panel name="flowMetrics">
                <FlowMetrics />
            </q-tab-panel>
            <q-tab-panel name="monthlyMeanFlow">
                <MonthlyMeanFlow />
            </q-tab-panel>
            <q-tab-panel name="stage">
                <StreamflowStage 
                    :active-point="props.activePoint"
                />
            </q-tab-panel>
        </q-tab-panels>
    </div>
</template>
<script setup>
import SevenDayFlow from "./SevenDayFlow.vue";
import FlowDurationTool from "./FlowDurationTool.vue";
import FlowMetrics from "./FlowMetrics.vue";
import MonthlyMeanFlow from "./MonthlyMeanFlow.vue";
import StreamflowStage from "./StreamflowStage.vue";
import { computed, ref } from 'vue';

const emit = defineEmits(['close']);

const props = defineProps({
    reportOpen: {
        type: Boolean,
        default: false,
    },
    activePoint: {
        type: Object,
        default: () => {},
    }
});

const viewPage = ref('sevenDayFlow');

const startYear = computed(() => { 
    return JSON.parse(props.activePoint.yr)[0];
})
const endYear = computed(() => { 
    return JSON.parse(props.activePoint.yr)[1];
})

</script>

<style lang="scss">
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
