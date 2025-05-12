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
                <div v-if="'net' in props.activePoint" class="col">
                    <div class="text-h6">Network</div>
                    <p>{{ props.activePoint.network }}</p>
                </div>
                <div v-if="'yr' in props.activePoint" class="col">
                    <div class="text-h6">Year Range</div>
                    <p>
                        {{ startYear }} - {{ endYear }}
                    </p>
                </div>
            </div>
            <q-separator color="white" />
            <q-list class="q-mt-sm">
                <q-item 
                    clickable 
                    :class="viewPage === 'surfaceWaterQuality' ? 'active' : ''"
                    @click="() => (viewPage = 'surfaceWaterQuality')"
                >
                    <div class="text-h6">Surface Water Quality</div>
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
                class="water-quality-panel"
                name="surfaceWaterQuality"
            >
                <div class="page-header text-h4">
                    Surface Water Quality
                </div>
                <div  class="surface-water-quality-table">
                    <table>
                        <tbody>
                            <!-- rows of data in the response array -->
                            <tr>
                                <th class="header-text">
                                    Parameter
                                </th>
                                <th />
                                <th 
                                    v-if="chemistry.sparkline"
                                    class="header-text"
                                    :colspan="Math.max(...chemistry.sparkline.map(el => el.data.length))"
                                >
                                    Entries
                                </th>
                            </tr>
                            <tr 
                                v-for="(param, idx) in chemistry.sparkline"
                                :name="idx"
                            >
                                <td>
                                    {{ param.title }} ({{ param.units }})
                                </td>
                                <td>
                                    <div class="mini-chart">
                                        <div class="mini-chart-overlay">
                                            <q-btn
                                                class="chart-expand"
                                                icon="add"
                                                dense
                                                @click="() => selectChart(param)"
                                            />
                                        </div>
                                        <SurfaceWaterQualityMiniChart 
                                            :selected-point="props.activePoint"
                                            :chart-data="param.data"
                                            :chart-id="`surface-quality-chart-mini-${param.paramId}`"
                                        />
                                    </div>
                                </td>
                                <td 
                                    v-for="datapoint in chemistry.sparkline[idx].data"
                                    class="table-cell"
                                >
                                    <div class="text-bold">
                                        {{ formatHeaderDate(datapoint.d) }}
                                    </div>
                                    <q-separator />
                                    <div>
                                        {{ datapoint.v || 'No Data' }} 
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </q-tab-panel>
        </q-tab-panels>

        <q-dialog v-model="showChart">
            <q-card 
                v-if="selectedChartData"
                class="chart-popup"
            >
                <SurfaceWaterQualityReportChart
                    v-if="props.activePoint"
                    :selected-point="props.activePoint"
                    :chart-data="selectedChartData"
                    :chart-id="`surface-quality-coliform-chart-${selectedChartData.paramId}`"
                />
            </q-card>
        </q-dialog>
    </div>
</template>

<script setup>
import SurfaceWaterQualityReportChart from '@/components/surfacewater/SurfaceWaterQualityReportChart.vue';
import surfaceWaterChemistry from '@/constants/surfaceWaterChemistry.json';
import SurfaceWaterQualityMiniChart from '@/components/surfacewater/SurfaceWaterQualityMiniChart.vue';
import { computed, onMounted, ref } from 'vue';

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

const viewPage = ref('surfaceWaterQuality');
const loading = ref(false);
const chemistry = ref([]);
const showChart = ref(false);
const selectedChartData = ref({});

const startYear = computed(() => { 
    return JSON.parse(props.activePoint.yr)[0];
})
const endYear = computed(() => { 
    return JSON.parse(props.activePoint.yr)[1];
})

onMounted(async () => {
    loading.value = true;
    await getData();
    loading.value = false;
});

const getData = async () => {
    // add API call
    chemistry.value = surfaceWaterChemistry;
}

const selectChart = (data) => {
    selectedChartData.value = data;
    showChart.value = true;
}

/**
 * simple formatter function to move functionality out of the template
 * 
 * @param date - the date string to format
 */
const formatHeaderDate = (date) => {
    return `${new Date(date).toLocaleDateString('en-CA')}`
}
</script>

<style lang="scss" scoped>
.data-license {
    display: flex;
    height: 100%;
    align-items: end;
    text-decoration: underline;
}

.page-header {
    color: #777
}

.about {
    cursor: pointer;
}

.q-item {
    &.active {
        background-color: $primary-light;
    }
}

.water-quality-panel {
    overflow-x: hidden;
}

.surface-water-quality-table {
    overflow: auto;

    table {
        th:first-child{
            background-color: white;
            position: sticky;
            position: -webkit-sticky;
            left: 0;
            z-index: 2;
            top: 0;
        }
        th:nth-child(2){
            background-color: white;
            position: sticky;
            position: -webkit-sticky;
            left: 100px;
            z-index: 2;
            top: 0;
        }
        td:first-child {
            background-color: white;
            position: sticky;
            position: -webkit-sticky;
            left: 0;
            z-index: 2;
            top: 0;
        }
        td:nth-child(2) {
            background-color: white;
            position: sticky;
            position: -webkit-sticky;
            left: 100px;
            z-index: 2;
            top: 0;
        }
    }

    .header-text {
        color: grey;
    }
    th {
        padding: 8px;
        text-align: left;
    }

    td {
        padding: 8px;
        text-align: left;
        border-bottom: 1px solid #ddd;
    }
}

.chart-popup {
    min-width: 60rem;
}

.table-cell {
    min-width: 8em;

    div {
        display: flex;
        align-items: center;
        height: 2rem;
    }

}

.mini-chart {
    position: relative;

    .mini-chart-overlay {
        display: flex;
        align-items: center;
        justify-content: center;
        position: absolute;
        width: 100%;
        height: 100%;
        top: 0;
        left: 0;
        opacity: 0;
        background-color: rgba(0, 0, 0, 0.20);
        transition: all 0.2s ease-in;

        &:hover { 
            opacity: 1;
            transition: all 0.2s ease-in;
        }

        .chart-expand {
            height: 2rem;
            width: 2rem;
            background-color: rgba(255, 255, 255, 0.75);
        }
    }
}
</style>

