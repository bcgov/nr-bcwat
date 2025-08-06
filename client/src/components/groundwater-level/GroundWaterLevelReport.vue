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
                        :flip-order="true"
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
            color: '#FFA500'
        }],
        chartColor: "#FFA500",
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
const oneDay = 24 * 60 * 60 * 1000; // hours*minutes*seconds*milliseconds
const diffDays = Math.round(Math.abs((new Date(chartStart) - new Date(chartEnd)) / oneDay));

const groundwaterLevelData = computed(() => {
    const myData = [];
    try {
        let currentDate = new Date(chartStart);
        const entryDateX = new Date(props.reportData.hydrograph.current[0].d);
        let day = Math.floor((entryDateX - new Date(entryDateX.getFullYear(), 0, 0)) / oneDay) - 1;

        for (let i = 0; i < diffDays; i++) {
            const entry = props.reportData.hydrograph.current[i]
            const ordinalDay = props.reportData.hydrograph.historical[day];
            const entryDate = new Date(currentDate);

            myData.push({
                d: entryDate,
                v : entry ? entry.v : null,
                max: ordinalDay?.max,
                p75: ordinalDay?.p75,
                p50: ordinalDay?.a,
                p25: ordinalDay?.p25,
                min: ordinalDay?.min,
            });

            if (entryDate.getDate() === 31 && entryDate.getMonth() === 11) {
                day = 0;
            } else {
                day += 1;
            }
            currentDate.setDate(currentDate.getDate() + 1);
        }
    } catch (e) {
        console.warn(e);
    } finally {
        return myData;
    }
});

</script>

<style lang="scss">
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
