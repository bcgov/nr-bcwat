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
                {{ props.activePoint.name }}
            </div>
            <div class="text-h5 subtitle">ID: {{ props.activePoint.nid }}</div>
            <div 
                class="header-grid"
            >
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
                    :class="viewPage === 'hydrograph' ? 'active' : ''"
                    @click="() => (viewPage = 'hydrograph')"
                >
                    <div class="text-h6">Hydrograph</div>
                </q-item>
                <q-item
                    clickable
                    :class="viewPage === 'monthylMean' ? 'active' : ''"
                    @click="() => (viewPage = 'monthylMean')"
                >
                    <div class="text-h6">Monthly Mean Levels</div>
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
            <q-tab-panel name="hydrograph">
                <div class="q-pa-md">
                    <ClimateReportChart
                        v-if="groundwaterLevelData.length > 0"
                        :chart-data="groundwaterLevelData"
                        chart-mode=""
                        report-name="groundwater-level"
                        y-axis-label="Depth to Water (m)"
                        chart-units="m"
                    />
                </div>
            </q-tab-panel>
            <q-tab-panel name="monthlyMean">
                <div class="q-pa-md">
                    <MonthlyMeanFlowTable 
                        :table-data="monthlyMeanFlow"
                    />
                </div>
            </q-tab-panel>
        </q-tab-panels>
    </div>
</template>
<script setup>
import MonthlyMeanFlowTable from "@/components/MonthlyMeanFlowTable.vue";
import ClimateReportChart from "@/components/climate/report/ClimateReportChart.vue";
import { computed, ref } from "vue";

const emit = defineEmits(["close"]);

const props = defineProps({
    reportOpen: {
        type: Boolean,
        default: false,
    },
    reportData: {
        type: Object,
        default: () => {},
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

const viewPage = ref('hydrograph');

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
        return year[1];
    }
    return props.activePoint.yr[1];
});

const chartStart = new Date(new Date().setFullYear(new Date().getFullYear() - 1)).setDate(1);
const chartEnd = new Date(new Date().setMonth(new Date().getMonth() + 7)).setDate(0);

const groundwaterLevelData = computed(() => {
    const myData = [];
    try {
        let i = 0;
        let historicalMonth;
        let currentMax = null;
        for (let d = new Date(chartStart); d <= new Date(chartEnd); d.setDate(d.getDate() + 1)) {
            const day = Math.floor((d - new Date(d.getFullYear(), 0, 0)) / 1000 / 60 / 60 / 24);
            historicalMonth = props.reportData.historical[day % 365];
            if (i < props.reportData.current.length) {
                currentMax = props.reportData.current[i].v;
            } else {
                currentMax = null;
            }
            myData.push({
                d: new Date(d),
                v: currentMax,
            });
            i++;
        }
    } catch (e) {
        console.error(e);
    } finally {
        return myData;
    }
});
</script>

<style lang="scss">
.kms {
    max-height: 100vh;
    overflow-y: scroll;
}
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
