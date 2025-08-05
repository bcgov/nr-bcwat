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
                        v-if="manualSnowChartData.length"
                        id="manual-snow-survey-chart"
                        :chart-data="manualSnowChartData"
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
import { computed, ref, watch } from "vue";

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
const oneDay = 24 * 60 * 60 * 1000; // hours*minutes*seconds*milliseconds
const diffDays = Math.round(Math.abs((new Date(chartStart) - new Date(chartEnd)) / oneDay));

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
        units: '°C',
    }
});

const temperatureChartData = computed(() => {
    const myData = [];

    try {
        if (props.reportContent.temperature && (props.reportContent.temperature.current.length > 0 ||  props.reportContent.temperature.historical.length > 0)) {
            let currentDate = new Date(chartStart);
            const entryDateX = new Date(props.reportContent.temperature.current[0].d);
            let day = Math.floor((entryDateX - new Date(entryDateX.getFullYear(), 0, 0)) / oneDay) - 1;

            for (let i = 0; i < diffDays; i++) {
                const entry = props.reportContent.temperature.current[i]
                const ordinalDay = props.reportContent.temperature.historical[day];
                const currentMax = entry ? entry.max : null;
                const currentMin = entry ? entry.min : null;
                const entryDate = new Date(currentDate);

                myData.push({
                    d: entryDate,
                    currentMax,
                    currentMin,
                    max: ordinalDay?.maxp90,
                    p75: ordinalDay?.maxavg,
                    p50: null,
                    p25: ordinalDay?.minavg,
                    min: ordinalDay?.minp10,
                });

                if (entryDate.getDate() === 31 && entryDate.getMonth() === 11) {
                    day = 0;
                } else {
                    day += 1;
                }
                currentDate.setDate(currentDate.getDate() + 1);
            }
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
        if (props.reportContent.precipitation && (props.reportContent.temperature.current.length > 0 ||  props.reportContent.temperature.historical.length > 0)) {
            let currentDate = new Date(chartStart);
            const entryDateX = new Date(props.reportContent.precipitation.current[0].d);
            let day = Math.floor((entryDateX - new Date(entryDateX.getFullYear(), 0, 0)) / oneDay) - 1;

            for (let i = 0; i < diffDays; i++) {
                const entry = props.reportContent.precipitation.current[i];
                const ordinalDay = props.reportContent.precipitation.historical[day];
                const entryDate = new Date(currentDate);

                myData.push({
                    d: entryDate,
                    currentMax: entry ? entry.v : null,
                    currentMin: 0,
                    max: ordinalDay?.p90,
                    p75: ordinalDay?.p75,
                    p50: ordinalDay?.p50,
                    p25: ordinalDay?.p25,
                    min: ordinalDay?.p10,
                });

                if (entryDate.getDate() === 31 && entryDate.getMonth() === 11) {
                    day = 0;
                } else {
                    day += 1;
                }
                currentDate.setDate(currentDate.getDate() + 1);
            }
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
        if (props.reportContent.snow_on_ground_depth && (props.reportContent.snow_on_ground_depth.current.length > 0 ||  props.reportContent.snow_on_ground_depth.historical.length > 0)) {
            let currentDate = new Date(chartStart);
            const entryDateX = new Date(props.reportContent.snow_on_ground_depth.current[0].d);
            let day = Math.floor((entryDateX - new Date(entryDateX.getFullYear(), 0, 0)) / oneDay) - 1;

            for (let i = 0; i < diffDays; i++) {
                const entry = props.reportContent.snow_on_ground_depth.current[i]
                const ordinalDay = props.reportContent.snow_on_ground_depth.historical[day];
                const entryDate = new Date(currentDate);

                myData.push({
                    d: entryDate,
                    v : entry ? entry.v : null,
                    max: ordinalDay?.p90,
                    p75: ordinalDay?.p75,
                    p50: ordinalDay?.a,
                    p25: ordinalDay?.p25,
                    min: ordinalDay?.p10,
                });

                if (entryDate.getDate() === 31 && entryDate.getMonth() === 11) {
                    day = 0;
                } else {
                    day += 1;
                }
                currentDate.setDate(currentDate.getDate() + 1);
            }
        }     } catch (e) {
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
        if (props.reportContent.snow_on_ground_depth && (props.reportContent.snow_on_ground_depth.current.length > 0 || props.reportContent.snow_on_ground_depth.historical.length > 0 )) {
            let currentDate = new Date(chartStart);
            const entryDateX = new Date(props.reportContent.snow_water_equivalent.current[0].d);
            let day = Math.floor((entryDateX - new Date(entryDateX.getFullYear(), 0, 0)) / oneDay) - 1;

            for (let i = 0; i < diffDays; i++) {
                const entry = props.reportContent.snow_water_equivalent.current[i]
                const ordinalDay = props.reportContent.snow_water_equivalent.historical[day];
                const entryDate = new Date(currentDate);

                myData.push({
                    d: entryDate,
                    v : entry ? entry.v : null,
                    max: ordinalDay?.p90,
                    p75: ordinalDay?.p75,
                    p50: ordinalDay?.a,
                    p25: ordinalDay?.p25,
                    min: ordinalDay?.p10,
                });

                if (entryDate.getDate() === 31 && entryDate.getMonth() === 11) {
                    day = 0;
                } else {
                    day += 1;
                }
                currentDate.setDate(currentDate.getDate() + 1);
            }
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
        if (props.reportContent.manual_snow_survey && (props.reportContent.manual_snow_survey.current.length > 0 || props.reportContent.manual_snow_survey.historical.length > 0)) {
            let currentDate = new Date(chartStart);
            const entryDateX = new Date(props.reportContent.manual_snow_survey.current[0].d);
            let day = Math.floor((entryDateX - new Date(entryDateX.getFullYear(), 0, 0)) / oneDay) - 1;

            for (let i = 0; i < diffDays; i++) {
                const entry = props.reportContent.manual_snow_survey.current[i]
                const ordinalDay = props.reportContent.manual_snow_survey.historical[day];
                const entryDate = new Date(currentDate);

                myData.push({
                    d: entryDate,
                    currentMax : entry ? entry.v : null,
                    currentMin: 0,
                    max: ordinalDay?.p90,
                    p75: ordinalDay?.p75,
                    p50: ordinalDay?.p50,
                    p25: ordinalDay?.p25,
                    min: ordinalDay?.p10,
                });

                if (entryDate.getDate() === 31 && entryDate.getMonth() === 11) {
                    day = 0;
                } else {
                    day += 1;
                }
                currentDate.setDate(currentDate.getDate() + 1);
            }
        }
    } catch (e) {
        console.error(e);
    } finally {
        return myData;
    }
});

const currentReport = computed(() => {
    if (props.reportContent) {
        return props.reportContent;
    }
    return null;
});

// When the report changes, change the viewPage to whichever page has data
watch(currentReport, () => {
    if (temperatureChartData.value.length >= 1) {
        viewPage.value = 'temperature';
    }
    else if (precipitationChartData.value.length >= 1) {
        viewPage.value = 'precipitation';
    }
    else if (snowOnGroundChartData.value.length >= 1) {
        viewPage.value = 'snowOnGround';
    }
    else if (snowWaterChartData.value.length >= 1) {
        viewPage.value = 'snowWaterEquivalent';
    }
    else if (manualSnowChartData.value.length >= 1) {
        viewPage.value = 'manualSnowSurvey';
    }
    else {
        viewPage.value = 'temperature';
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
