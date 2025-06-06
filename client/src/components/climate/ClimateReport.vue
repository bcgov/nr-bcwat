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
            <q-list class="report-list q-mt-sm">
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
                <div class="q-pa-md">
                    <ReportChart
                        v-if="temperatureChartData.filter(entry => entry.currentMax !== null).length"
                        id="temperature-chart"
                        :chart-data="temperatureChartData"
                        :chart-options="temperatureChartOptions"
                    />
                    <p v-else>No Data Available</p>
                </div>
            </q-tab-panel>
            <q-tab-panel name="precipitation">
                <div class="q-pa-md">
                    <ReportChart
                        v-if="precipitationChartData.filter(entry => entry.currentMax !== null).length"
                        id="precipitation-chart"
                        :chart-data="precipitationChartData"
                        :chart-options="precipitationChartOptions"
                    />
                    <p v-else>No Data Available</p>
                </div>
            </q-tab-panel>
            <q-tab-panel name="snowOnGround">
                <div class="q-pa-md">
                    <ReportChart
                        v-if="snowOnGroundChartData.filter(entry => entry.currentMax !== null).length"
                        id="snow-on-ground-chart"
                        :chart-data="snowOnGroundChartData"
                        :chart-options="snowOnGroundChartOptions"
                    />
                    <p v-else>No Data Available</p>
                </div>
            </q-tab-panel>
            <q-tab-panel name="snowWaterEquivalent">
                <div class="q-pa-md">
                    <ReportChart
                        v-if="snowWaterChartData.filter(entry => entry.currentMax !== null).length"
                        id="snow-water-equivalent-chart"
                        :chart-data="snowWaterChartData"
                        :chart-options="snowWaterChartOptions"
                    />
                    <p v-else>No Data Available</p>
                </div>
            </q-tab-panel>
            <q-tab-panel name="manualSnowSurvey">
                <div class="q-pa-md">
                    <ReportChart
                        v-if="manualSnowChartData.filter((entry) => entry.max !== null || entry.currentMax !== null).length"
                        id="manual-snow-survey-chart"
                        :chart-data="manualSnowChartData"
                        :chart-options="manualSnowChartOptions"
                    />
                    <p v-else>No Data Available</p>
                </div>
            </q-tab-panel>
        </q-tab-panels>
    </div>
</template>
<script setup>
import ReportChart from '@/components/ReportChart.vue';
import { computed, ref } from "vue";
import manualSnow from "@/constants/manualSnow.json";

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
        required: true,
    },
});

const viewPage = ref("temperature");

const startYear = computed(() => {
    if(!props.activePoint) return new Date().getFullYear();
    if(typeof props.activePoint.yr === 'string'){
        const year = JSON.parse(props.activePoint.yr);
        return year[0];
    }
    return props.activePoint.yr[0];
});
const endYear = computed(() => {
    if(!props.activePoint) return new Date().getFullYear();
    if(typeof props.activePoint.yr === 'string'){
        const year = JSON.parse(props.activePoint.yr);
        return year[1];
    }
    return props.activePoint.yr[1];
});

const chartStart = new Date(new Date().setFullYear(new Date().getFullYear() - 1)).setDate(1);
const chartEnd = new Date(new Date().setMonth(new Date().getMonth() + 7)).setDate(0);
const temperatureChartOptions = computed(() => {
    return {
        name: 'temperature',
        startYear: startYear.value, 
        endYear: endYear.value,
        legend: [
            {
                label: "Current Max",
                color: "#b3d4fc",
            },
            {
                label: "Current Min",
                color: "#b3d4fc",
            }
        ],
        yLabel: 'Temperature (°C)',
        units: '°C'
    }
});

const temperatureChartData = computed(() => {
    const myData = [];
    try {
        let i = 0;
        let historicalMonth;
        let currentMax = null;
        let currentMin = null;

        if(props.reportContent){
            for (
                let d = new Date(chartStart);
                d <= new Date(chartEnd);
                d.setDate(d.getDate() + 1)
            ) {
                const day = Math.floor((d - new Date(d.getFullYear(), 0, 0)) / 1000 / 60 / 60 / 24);
                historicalMonth = props.reportContent.temperature.historical[day % 365];
                if (i < props.reportContent.temperature.current.length) {
                    currentMax = props.reportContent.temperature.current[i].max;
                    currentMin = props.reportContent.temperature.current[i].min;
                } else {
                    currentMax = null;
                    currentMin = null;
                }
                myData.push({
                    d: new Date(d),
                    currentMax: currentMax,
                    currentMin: currentMin,
                    max: historicalMonth?.maxp90,
                    min: historicalMonth?.minp10,
                    p25: historicalMonth?.minavg,
                    p50: null,
                    p75: historicalMonth?.maxavg,
                });
                i++;
            }
        } else {
            return [];
        }
    } catch (e) {
        console.error(e);
    } finally {
        return myData;
    }
});

const precipitationChartOptions = computed(() => {
    return {
        name: 'precipitation',
        startYear: startYear.value, 
        endYear: endYear.value,
        legend: [
            {
                label: "Current MTD",
                color: "#b3d4fc",
            },
        ],
        yLabel: 'Precipitation (mm)',
        units: 'mm'
    }
});

const precipitationChartData = computed(() => {
    const myData = [];
    try {
        let i = 0;
        let currentMonth = 0;
        let total = 0;
        let historicalMonth;
        for (
            let d = new Date(chartStart);
            d <= new Date(chartEnd);
            d.setDate(d.getDate() + 1)
        ) {
            if (d.getMonth() !== currentMonth) {
                currentMonth = d.getMonth();
                total = 0;
                historicalMonth =
                    props.reportContent.precipitation.historical.find(
                        (entry) => entry.d === d.getMonth() + 1
                    );
            }
            if (
                d.toDateString() ===
                new Date(
                    props.reportContent.precipitation.current[i]?.d
                ).toDateString()
            ) {
                total += props.reportContent.precipitation.current[i].v;
            }
            if (d > new Date()) {
                total = null;
            }
            myData.push({
                d: new Date(d),
                currentMax: total,
                currentMin: 0,
                max: historicalMonth?.p90,
                min: historicalMonth?.p10,
                p25: historicalMonth?.p25,
                p50: historicalMonth?.p50,
                p75: historicalMonth?.p75,
            });
            i++;
        }
    } catch (e) {
        console.error(e);
    } finally {
        return myData;
    }
});

const snowOnGroundChartOptions = computed(() => {
    return {
        name: 'snow-on-ground',
        startYear: startYear.value, 
        endYear: endYear.value,
        legend: [
            {
                label: "Current Snow Depth",
                color: "#b3d4fc",
            },
        ],
        yLabel: 'Snow Depth (cm)',
        units: 'cm'
    }
});

const snowOnGroundChartData = computed(() => {
    const myData = [];
    try {
        let i = 0;
        let historicalMonth;
        let currentMax = null;
        for (
            let d = new Date(chartStart);
            d <= new Date(chartEnd);
            d.setDate(d.getDate() + 1)
        ) {
            const day = Math.floor((d - new Date(d.getFullYear(), 0, 0)) / 1000 / 60 / 60 / 24);
            historicalMonth = props.reportContent.snow_on_ground_depth.historical[day % 365];
            if (i < props.reportContent.snow_on_ground_depth.current.length) {
                currentMax = props.reportContent.snow_on_ground_depth.current[i].v;
            } else {
                currentMax = null;
            }
            myData.push({
                d: new Date(d),
                currentMax: currentMax,
                currentMin: 0,
                max: historicalMonth?.p90,
                min: historicalMonth?.p10,
                p25: historicalMonth?.p25,
                p50: historicalMonth?.a,
                p75: historicalMonth?.p75,
            });
            i++;
        }
    } catch (e) {
        console.error(e);
    } finally {
        return myData;
    }
});

const snowWaterChartOptions = computed(() => {
    return {
        name: 'snow-on-ground',
        startYear: startYear.value, 
        endYear: endYear.value,
        legend: [
            {
                label: "Current Snow Water Equiv.",
                color: "#b3d4fc",
            },
        ],
        yLabel: 'Snow Water Equiv. (cm)',
        units: 'cm'
    }
});

const snowWaterChartData = computed(() => {
    const myData = [];
    try {
        let i = 0;
        let historicalMonth;
        let currentMax = null;
        for (
            let d = new Date(chartStart);
            d <= new Date(chartEnd);
            d.setDate(d.getDate() + 1)
        ) {
            const day = Math.floor((d - new Date(d.getFullYear(), 0, 0)) / 1000 / 60 / 60 / 24);
            historicalMonth = props.reportContent.snow_water_equivalent.historical[day % 365];
            if (i < props.reportContent.snow_water_equivalent.current.length) {
                currentMax = props.reportContent.snow_water_equivalent.current[i].v;
            } else {
                currentMax = null;
            }
            myData.push({
                d: new Date(d),
                currentMax: currentMax,
                currentMin: 0,
                max: historicalMonth?.p90,
                min: historicalMonth?.p10,
                p25: historicalMonth?.p25,
                p50: historicalMonth?.a,
                p75: historicalMonth?.p75,
            });
            i++;
        }
    } catch (e) {
        console.error(e);
    } finally {
        return myData;
    }
});


const manualSnowChartOptions = computed(() => {
    return {
        name: 'manual-snow',
        startYear: startYear.value, 
        endYear: endYear.value,
        legend: [],
        yLabel: 'Manual Snow',
        units: 'cm'
    }
});

const manualSnowChartData = computed(() => {
    const myData = [];
    try {
        let i = 0;
        let historicalMonth;
        let currentMax = null;
        for (let d = new Date(chartStart); d <= new Date(chartEnd); d.setDate(d.getDate() + 1)) {
            const day = Math.floor((d - new Date(d.getFullYear(), 0, 0)) / 1000 / 60 / 60 / 24);
            historicalMonth = manualSnow.historical[day % 365];
            if (i < manualSnow.current.length) {
                currentMax = manualSnow.current[i].v;
            } else {
                currentMax = null;
            }
            myData.push({
                d: new Date(d),
                currentMax: currentMax,
                currentMin: 0,
                max: historicalMonth?.p90,
                min: historicalMonth?.p10,
                p25: historicalMonth?.p25,
                p50: historicalMonth?.p50,
                p75: historicalMonth?.p75,
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
