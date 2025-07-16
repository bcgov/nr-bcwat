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
                    :class="viewPage === 'monthlyMean' ? 'active' : ''"
                    @click="() => (viewPage = 'monthlyMean')"
                >
                    <div class="text-h6">Monthly Mean Levels</div>
                </q-item>
            </q-list>
            <div>
                <span class="about">
                    <q-icon name="help" /> About this page
                    <q-tooltip>About this page content goes here.</q-tooltip>
                </span>
            </div>
            <div class="data-license cursor-pointer">Data License</div>
        </div>
        <q-tab-panels v-model="viewPage">
            <q-tab-panel name="hydrograph">
                <div class="q-pa-md">
                    <ReportChart
                        v-if="props.reportData && 'hydrograph' in props.reportData && props.reportData.hydrograph.current.length"
                        :chart-data="groundwaterLevelData"
                        :historical-chart-data="historicalGroundwaterLevelData"
                        :chart-options="chartOptions"
                        :active-point="props.activePoint"
                        yearly-type="groundwaterlevel"
                        chart-type="hydrograph"
                        chart-name="hydrograph"
                    />
                </div>
            </q-tab-panel>
            <q-tab-panel name="monthlyMean">
                <div class="q-pa-md">
                    <MonthlyMeanFlowTable 
                        v-if="props.reportData && 'monthly_mean_flow' in props.reportData && props.reportData.monthly_mean_flow"
                        :table-data="props.reportData.monthly_mean_flow"
                    />
                </div>
            </q-tab-panel>
        </q-tab-panels>
    </div>
</template>
<script setup>
import MonthlyMeanFlowTable from "@/components/MonthlyMeanFlowTable.vue";
import ReportChart from "@/components/ReportChart.vue";
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
    activePoint: {
        type: Object,
        default: () => {},
    },
});

const viewPage = ref('hydrograph');

const chartOptions = computed(() => {
    return {
        name: 'groundwater-level',
        units: 'm',
        startYear: startYear.value,
        endYear: endYear.value,
        yLabel: 'Depth to Water (m)',
        legend: [{
            label: 'Current',
            color: 'orange'
        }],
    }
});

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
    return props.activePoint.yr[props.activePoint.yr.length - 1];
});

const chartStart = new Date(new Date().setFullYear(new Date().getFullYear() - 1)).setDate(1);
const chartEnd = new Date(new Date().setMonth(new Date().getMonth() + 7)).setDate(0);

const groundwaterLevelData = computed(() => {
    const data = [];
    try {
        for (let d = new Date(chartStart); d <= new Date(chartEnd); d.setDate(d.getDate() + 1)) {
            let valToAdd = null;

            const valueForDate = props.reportData.hydrograph.current.find(el => {
                return (d.getDate() === new Date(el.d).getDate()) && 
                    (d.getMonth() === new Date(el.d).getMonth()) && 
                    (d.getFullYear() === new Date(el.d).getFullYear());
            })

            if(valueForDate?.v){
                valToAdd = valueForDate.v;
            }

            data.push({
                d: new Date(d),
                v: valToAdd
            });
        }
    } catch (e) {
        console.warn(e);
    } finally {
        return data;
    }
});

const historicalGroundwaterLevelData = computed(() => {
    const myData = [];
    try {
        let i = 0;
        let currentMax = null;
        for (let d = new Date(chartStart); d <= new Date(chartEnd); d.setDate(d.getDate() + 1)) {
            const day = Math.floor((d - new Date(d.getFullYear(), 0, 0)) / 1000 / 60 / 60 / 24);
            const dataLength = props.reportData.hydrograph.historical.length;
            // note: setting to 365 will correctly set the data, we expect the data to be filled from d: 1 to d: 365 always. 
            // const dataLength = 365
            const month = props.reportData.hydrograph.historical[day % 365];

            if (i < props.reportData.hydrograph.historical.length) {
                currentMax = props.reportData.hydrograph.historical[i].v;
            } else {
                currentMax = null;
            }

            myData.push({
                d: new Date(d),
                max: month.max,
                min: month.min,
                p75: month.p75,
                p50: month.a,
                p25: month.p25,
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
    height: 100%;
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
