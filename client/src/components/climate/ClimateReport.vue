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
                    data-cy="back-to-map"
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
                    :disable="temperatureChartData.length < 1"
                    @click="() => (viewPage = 'temperature')"
                >
                    <div class="text-h6">Temperature</div>
                </q-item>
                <q-item
                    clickable
                    :class="viewPage === 'precipitation' ? 'active' : ''"
                    :disable="precipitationChartData.length < 1"
                    @click="() => (viewPage = 'precipitation')"
                >
                    <div class="text-h6">Precipitation</div>
                </q-item>
                <q-item
                    clickable
                    :class="viewPage === 'snowOnGround' ? 'active' : ''"
                    :disable="snowOnGroundChartData.length < 1"
                    @click="() => (viewPage = 'snowOnGround')"
                >
                    <div class="text-h6">Snow on Ground</div>
                </q-item>
                <q-item
                    clickable
                    :class="viewPage === 'snowWaterEquivalent' ? 'active' : ''"
                    :disable="snowWaterChartData.length < 1"
                    @click="() => (viewPage = 'snowWaterEquivalent')"
                >
                    <div class="text-h6">Snow Water Equivalent</div>
                </q-item>
                <q-item
                    clickable
                    :class="viewPage === 'manualSnowSurvey' ? 'active' : ''"
                    :disable="manualSnowChartData.length < 1"
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
                        v-if="props.activePoint && temperatureChartData.length"
                        id="temperature-chart"
                        :chart-data="temperatureChartData"
                        :chart-options="temperatureChartOptions"
                        :active-point="props.activePoint"
                        chart-type="temperature"
                        chart-name="temperature"
                        :historical-chart-data="temperatureChartData"
                        :station-name="props.activePoint.name"
                        yearly-type="climate"
                    />
                    <div
                        v-else
                        class="no-data"
                    >
                        <q-card class="q-pa-sm text-center">
                            <div>No Data Available</div>
                        </q-card>
                    </div>
                </div>
            </q-tab-panel>
            <q-tab-panel name="precipitation">
                <div class="q-pa-md">
                    <ReportChart
                        v-if="precipitationChartData.length"
                        id="precipitation-chart"
                        :chart-data="precipitationChartData"
                        :historical-chart-data="precipitationChartData"
                        :chart-options="precipitationChartOptions"
                        :active-point="props.activePoint"
                        chart-type="precipitation"
                        chart-name="precipitation"
                        :station-name="props.activePoint.name"
                        yearly-type="climate"
                    />
                    <div
                        v-else
                        class="no-data"
                    >
                        <q-card class="q-pa-sm text-center">
                            <div>No Data Available</div>
                        </q-card>
                    </div>
                </div>
            </q-tab-panel>
            <q-tab-panel name="snowOnGround">
                <div class="q-pa-md">
                    <ReportChart
                        v-if="snowOnGroundChartData.length"
                        id="snow-on-ground-chart"
                        :chart-data="snowOnGroundChartData"
                        :historical-chart-data="snowOnGroundChartData"
                        :chart-options="snowOnGroundChartOptions"
                        :active-point="props.activePoint"
                        chart-type="snow-depth"
                        chart-name="snow_on_ground_depth"
                        :station-name="props.activePoint.name"
                        yearly-type="climate"
                    />
                    <div
                        v-else
                        class="no-data"
                    >
                        <q-card class="q-pa-sm text-center">
                            <div>No Data Available</div>
                        </q-card>
                    </div>
                </div>
            </q-tab-panel>
            <q-tab-panel name="snowWaterEquivalent">
                <div class="q-pa-md">
                    <ReportChart
                        v-if="snowWaterChartData.length"
                        id="snow-water-equivalent-chart"
                        :chart-data="snowWaterChartData"
                        :historical-chart-data="snowWaterChartData"
                        :chart-options="snowWaterChartOptions"
                        :active-point="props.activePoint"
                        chart-type="snow-water-equivalent"
                        chart-name="snow_water_equivalent"
                        :station-name="props.activePoint.name"
                        yearly-type="climate"
                    />
                    <div
                        v-else
                        class="no-data"
                    >
                        <q-card class="q-pa-sm text-center">
                            <div>No Data Available</div>
                        </q-card>
                    </div>
                </div>
            </q-tab-panel>
            <q-tab-panel name="manualSnowSurvey">
                <div class="q-pa-md">
                    <ReportChart
                        v-if="manualSnowChartData.filter((entry) => entry.max).length"
                        id="manual-snow-survey-chart"
                        :chart-data="manualSnowChartData"
                        :historical-chart-data="manualSnowChartData"
                        :chart-options="manualSnowChartOptions"
                        :active-point="props.activePoint"
                        chart-type="snow-survey"
                        chart-name="manual_snow_survey"
                        :station-name="props.activePoint.name"
                        yearly-type="climate"
                    />
                    <div
                        v-else
                        class="no-data"
                    >
                        <q-card class="q-pa-sm text-center">
                            <div>No Data Available</div>
                        </q-card>
                    </div>
                </div>
            </q-tab-panel>
        </q-tab-panels>
    </div>
</template>
<script setup>
import ReportChart from '@/components/ReportChart.vue';
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
        required: true,
    },
});

const viewPage = ref("temperature");

const startYear = computed(() => {
    if (!props.activePoint) return new Date().getFullYear();
    if (typeof props.activePoint.yr === 'string') {
        const year = JSON.parse(props.activePoint.yr);
        return year[0];
    }
    return props.activePoint.yr[0];
});
const endYear = computed(() => {
    if (!props.activePoint) return new Date().getFullYear();
    if (typeof props.activePoint.yr === 'string') {
        const yearArr = JSON.parse(props.activePoint.yr);
        return yearArr[yearArr.length - 1];
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
                color: "#FFA500",
            },
            {
                label: "Current Min",
                color: "#FFA500",
            }
        ],
        chartColor: "#FFA500",
        yLabel: 'Temperature (°C)',
        units: '°C'
    }
});

const temperatureChartData = computed(() => {
    const myData = [];
    try {
        if (props.reportContent.temperature) {
            props.reportContent.temperature.current.forEach((entry) => {

                const entryDate = new Date(entry.d)
                const day = Math.floor((entryDate - new Date(entryDate.getFullYear(), 0, 0)) / 1000 / 60 / 60 / 24);
                const ordinalDay = props.reportContent.temperature.historical[day % 365];

                myData.push({
                    d: entryDate,
                    currentMax: entry.max,
                    currentMin: entry.min,
                    max: ordinalDay?.maxp90,
                    min: ordinalDay?.minp10,
                    p25: ordinalDay?.minavg,
                    p50: null,
                    p75: ordinalDay?.maxavg,
                });
            })
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
        chartColor: "#b3d4fc",
        yLabel: 'Precipitation (mm)',
        units: 'mm'
    }
});

const precipitationChartData = computed(() => {
    const myData = [];
    try {
        if (props.reportContent.precipitation) {
            props.reportContent.precipitation.current.forEach((entry) => {

                const entryDate = new Date(entry.d)
                const day = Math.floor((entryDate - new Date(entryDate.getFullYear(), 0, 0)) / 1000 / 60 / 60 / 24);
                const ordinalDay = props.reportContent.precipitation.historical[day % 365];

                myData.push({
                    d: entryDate,
                    currentMax: entry.v,
                    currentMin: 0,
                    max: ordinalDay?.p90,
                    min: ordinalDay?.p10,
                    p25: ordinalDay?.p25,
                    p50: ordinalDay?.p50,
                    p75: ordinalDay?.p75,
                });
            })
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
        chartColor: "#b3d4fc",
        yLabel: 'Snow Depth (cm)',
        units: 'cm'
    }
});

const snowOnGroundChartData = computed(() => {
    const myData = [];
    try {
        if (props.reportContent.snow_on_ground_depth) {
            props.reportContent.snow_on_ground_depth.current.forEach((entry) => {

                const entryDate = new Date(entry.d)
                const day = Math.floor((entryDate - new Date(entryDate.getFullYear(), 0, 0)) / 1000 / 60 / 60 / 24);
                const ordinalDay = props.reportContent.snow_on_ground_depth.historical[day % 365];

                myData.push({
                    d: entryDate,
                    currentMax: entry.v,
                    currentMin: 0,
                    max: ordinalDay?.p90,
                    min: ordinalDay?.p10,
                    p25: ordinalDay?.p25,
                    p50: ordinalDay?.a,
                    p75: ordinalDay?.p75,
                });
            })
        } else {
            return [];
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
        chartColor: "#b3d4fc",
        yLabel: 'Snow Water Equiv. (cm)',
        units: 'cm'
    }
});

const snowWaterChartData = computed(() => {
    const myData = [];
    try {
        if (props.reportContent.snow_water_equivalent) {
            props.reportContent.snow_water_equivalent.current.forEach((entry) => {

                const entryDate = new Date(entry.d)
                const day = Math.floor((entryDate - new Date(entryDate.getFullYear(), 0, 0)) / 1000 / 60 / 60 / 24);
                const ordinalDay = props.reportContent.snow_water_equivalent.historical[day % 365];

                myData.push({
                    d: entryDate,
                    currentMax: entry.v,
                    currentMin: 0,
                    max: ordinalDay?.p90,
                    min: ordinalDay?.p10,
                    p25: ordinalDay?.p25,
                    p50: ordinalDay?.a,
                    p75: ordinalDay?.p75,
                });
            })
        } else {
            return [];
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
        chartColor: "#b3d4fc",
        yLabel: 'Manual Snow',
        units: 'cm'
    }
});

const manualSnowChartData = computed(() => {
    const myData = [];
    try {
        if (props.reportContent.manual_snow_survey) {
            props.reportContent.manual_snow_survey.current.forEach((entry) => {

                const entryDate = new Date(entry.d)
                const day = Math.floor((entryDate - new Date(entryDate.getFullYear(), 0, 0)) / 1000 / 60 / 60 / 24);
                const ordinalDay = props.reportContent.manual_snow_survey.historical[day % 365];

                myData.push({
                    d: entryDate,
                    currentMax: entry.v,
                    currentMin: 0,
                    max: ordinalDay?.p90,
                    min: ordinalDay?.p10,
                    p25: ordinalDay?.p25,
                    p50: ordinalDay?.a,
                    p75: ordinalDay?.p75,
                });
            })
        } else {
            return [];
        }
    } catch (e) {
        console.error(e);
    } finally {
        return myData;
    }
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
.no-data {
    display: flex;
    width: 100%;
    height: 100%;
    align-items: center;
    justify-content: center;
}
</style>
