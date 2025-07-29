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
                <div v-if="'area' in props.activePoint" class="col">
                    <div class="text-h6">Area</div>
                    <p>{{ props.activePoint.area }} km<sup>2</sup></p>
                </div>
                <div v-if="'net' in props.activePoint" class="col">
                    <div class="text-h6">Mean Annual Discharge</div>
                    <p>{{ props.reportData?.meanAnnualFlow }} m<sup>3</sup>/s</p>
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
                        v-if="props.activePoint && ('sevenDayFlow' in props.reportData)"
                        :chart-data="props.reportData.sevenDayFlow"
                        :selected-point="props.activePoint"
                    />
                </div>
            </q-tab-panel>
            <q-tab-panel name="flowDurationTool">
                <FlowDurationTool
                    v-if="props.reportData.flowDuration"
                    :chart-data="props.reportData.flowDuration"
                />
            </q-tab-panel>
            <q-tab-panel name="flowMetrics">
                <FlowMetrics
                    v-if="props.reportData.flowMetrics"
                    :table-data="props.reportData.flowMetrics"
                />
            </q-tab-panel>
            <q-tab-panel name="monthlyMeanFlow">
                <MonthlyMeanFlowTable
                    v-if="props.reportData.monthlyMeanFlow"
                    :table-data="props.reportData.monthlyMeanFlow"
                />
            </q-tab-panel>
            <q-tab-panel name="stage">
                <StreamflowStage
                    :chart-data="props.reportData.sevenDayFlow"
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
})
const endYear = computed(() => {
    if(typeof props.activePoint.yr === 'string'){
        const year = JSON.parse(props.activePoint.yr);
        return year[year.length - 1];
    }
    return props.activePoint.yr[1];
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

.q-tab-panels {
    padding: 1rem;
}

.q-item {
    &.active {
        background-color: $primary-light;
    }
}
</style>
