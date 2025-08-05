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
                {{ props.activePoint.name }}
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
                <div v-if="'area' in props.activePoint && props.activePoint.area > 0" class="col">
                    <div class="text-h6">Area</div>
                    <p>{{ props.activePoint.area }} km<sup>2</sup></p>
                </div>
                <div v-if="'meanAnnualFlow' in props.reportData && props.reportData.meanAnnualFlow !== null" class="col">
                    <div class="text-h6">Mean Annual Discharge</div>
                    <p>{{ props.reportData?.meanAnnualFlow?.toFixed(2) }} m<sup>3</sup>/s</p>
                </div>
            </div>
            <q-separator color="white" />
            <q-list class="q-mt-sm">
                <q-item
                    clickable
                    :disable="!hasSevenDay"
                    :class="viewPage === 'sevenDayFlow' ? 'active' : ''"
                    @click="() => (viewPage = 'sevenDayFlow')"
                >
                    <div class="text-h6">Seven Day Flow</div>
                </q-item>
                <q-item
                    clickable
                    :disable="!hasFlowDuration"
                    :class="viewPage === 'flowDurationTool' ? 'active' : ''"
                    @click="() => (viewPage = 'flowDurationTool')"
                >
                    <div class="text-h6">Flow Duration Tool</div>
                </q-item>
                <q-item
                    clickable
                    :disable="!props.reportData.hasFlowMetrics"
                    :class="viewPage === 'flowMetrics' ? 'active' : ''"
                    @click="() => (viewPage = 'flowMetrics')"
                >
                    <div class="text-h6">Flow Metrics</div>
                </q-item>
                <q-item
                    clickable
                    :disable="!hasMonthlyMeanFlow"
                    :class="viewPage === 'monthlyMeanFlow' ? 'active' : ''"
                    @click="() => (viewPage = 'monthlyMeanFlow')"
                >
                    <div class="text-h6">Monthly Mean Flow</div>
                </q-item>
                <q-item
                    clickable
                    :disable="!hasStage"
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
            <q-tab-panel
                v-if="hasSevenDay"
                name="sevenDayFlow"
            >
                <div class="q-ma-md full-height">
                    <SevenDayFlow
                        v-if="props.activePoint && hasSevenDay"
                        :chart-data="props.reportData.sevenDayFlow"
                        :selected-point="props.activePoint"
                    />
                </div>
            </q-tab-panel>
            <q-tab-panel name="flowDurationTool">
                <FlowDurationTool
                    v-if="props.reportData.flowDurationTool && hasFlowDuration"
                    :chart-data="props.reportData.flowDurationTool"
                />
            </q-tab-panel>
            <q-tab-panel name="flowMetrics">
                <FlowMetrics
                    v-if="props.reportData.flowMetrics && props.reportData.hasFlowMetrics"
                    :table-data="props.reportData.flowMetrics"
                />
            </q-tab-panel>
            <q-tab-panel name="monthlyMeanFlow">
                <MonthlyMeanFlowTable
                    v-if="props.reportData.monthlyMeanFlow && hasMonthlyMeanFlow"
                    :table-data="props.reportData.monthlyMeanFlow"
                />
            </q-tab-panel>
            <q-tab-panel name="stage">
                <StreamflowStage
                    v-if = "props.reportData.hasStationMetrics"
                    :chart-data="props.reportData.stage"
                    :selected-point="props.activePoint"
                />
            </q-tab-panel>
        </q-tab-panels>
    </div>
</template>
<script setup>
import SevenDayFlow from "@/components/streamflow/SevenDayFlow.vue";
import FlowDurationTool from "@/components/streamflow//FlowDurationTool.vue";
import FlowMetrics from "@/components/streamflow/FlowMetrics.vue";
import MonthlyMeanFlowTable from "@/components/MonthlyMeanFlowTable.vue";
import StreamflowStage from "@/components/streamflow/StreamflowStage.vue";
import { computed, ref, watch } from 'vue';

const emit = defineEmits(['close']);

const props = defineProps({
    reportOpen: {
        type: Boolean,
        default: false,
    },
    reportData: {
        type: Object,
        default: () => {},
    },
    activePoint: {
        type: Object,
        default: () => {},
    }
});

const viewPage = ref('sevenDayFlow');


const startYear = computed(() => {
    if(typeof props.activePoint.yr === 'string'){
        const year = JSON.parse(props.activePoint.yr);
        return year[0];
    }
    return props.activePoint.yr[0];
});

const endYear = computed(() => {
    if(typeof props.activePoint.yr === 'string'){
        const year = JSON.parse(props.activePoint.yr);
        return year[year.length - 1];
    }
    return props.activePoint.yr[1];
});

const hasSevenDay = computed(() => {
    if ("sevenDayFlow" in props.reportData) {
        return props.reportData.sevenDayFlow.current.length > 0 || props.reportData.sevenDayFlow.historical.length > 0;
    } else {
        return false;
    }
});

const hasFlowDuration = computed(() => {
    if ("flowDurationTool" in props.reportData) {
        return props.reportData.flowDurationTool.length > 0;
    } else {
        return false;
    }
});

const hasMonthlyMeanFlow = computed(() => {
    if ("monthlyMeanFlow" in props.reportData) {
        return props.reportData.monthlyMeanFlow.terms.length > 0 || props.reportData.monthlyMeanFlow.years.length > 0;
    } else {
        return false;
    }
});

const hasStage = computed(() => {
    if ("stage" in props.reportData) {
        return props.reportData.stage.current.length > 0 || props.reportData.stage.historical.length > 0;
    } else {
        return false;
    }
})

const currentReport = computed(() => {
    if (props.reportData) {
        return props.reportData;
    }
    return null;
});

// When the report changes, change the viewPage to whichever page has data
watch(currentReport, () => {
    if (hasSevenDay.value) {
        viewPage.value = 'sevenDayFlow';
    }
    else if (hasFlowDuration.value) {
        viewPage.value = 'flowDurationTool';
    }
    else if (props.reportData?.hasFlowMetrics) {
        viewPage.value = 'flowMetrics';
    }
    else if (hasMonthlyMeanFlow.value) {
        viewPage.value = 'monthlyMeanFlow';
    }
    else if (hasStage.value) {
        viewPage.value = 'stage';
    }
    else {
        viewPage.value = 'sevenDayFlow';
    }
});

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

.q-tab-panels {
    padding: 1rem;
}

.q-item {
    &.active {
        background-color: $primary-light;
    }
}
</style>
