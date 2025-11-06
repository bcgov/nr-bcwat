<template>
    <div class="map-filters-container">
        <div class="q-pa-sm">
            <div v-if="localFilters.buttons">
                <div class="map-filters-header">
                    {{ props.title }}
                </div>
                <p>{{ props.paragraph }}</p>
                <q-checkbox
                    v-for="button in localFilters.buttons"
                    :key="button"
                    v-model="button.value"
                    :label="button.label"
                    :color="button.color"
                    @update:model-value="emit('update-filter', localFilters)"
                />
            </div>
            <div v-if="props.page === 'watershed'">
                <q-avatar color="grey-4" text-color="primary" icon="mdi-map-marker" size="lg"/> Current Application
                <q-avatar color="grey-4" text-color="warning" icon="mdi-map-marker" size="lg"/> Active Application
            </div>
            <q-card
                v-if="activePoint"
                class="selected-point q-pa-sm q-ma-sm"
                flat
                bordered
            >
                <q-item v-if="props.page === 'watershed'">
                    <q-item-section avatar>
                        <q-avatar color="grey-4" :text-color="activePoint.properties.st === 'ACTIVE APPL.' ? 'warning' : 'primary'" icon="mdi-map-marker"/>
                    </q-item-section>
                    <q-item-section>
                        <div
                            v-if="'lic' in activePoint.properties"
                            class="text-h6"
                        >
                            {{ activePoint.properties.lic }}<span v-if="'nid' in activePoint.properties">, {{ activePoint.properties.nid }}</span>
                        </div>
                        <div v-if="'qty' in activePoint.properties && activePoint.properties.qty > 0">
                            Quantity: {{ activePoint.properties.qty }} m<sup>3</sup>/year
                        </div>
                        <div v-if="'org' in activePoint.properties">
                            Licence Purpose: {{ activePoint.properties.org }}
                        </div>
                        <div v-if="'term' in activePoint.properties">
                            Term: {{ activePoint.properties.term }}
                        </div>
                    </q-item-section>
                </q-item>
                <div v-else>
                    <div
                        v-if="'name' in activePoint.properties"
                        class="text-bold"
                    >
                        {{ activePoint.properties.name }}
                    </div>
                    <div v-if="'nid' in activePoint.properties">
                        NID: {{ activePoint.properties.nid }}
                    </div>
                    <div v-if="'net' in activePoint.properties">
                        Network: {{ activePoint.properties.net }}
                    </div>
                    <div v-if="'yr' in activePoint.properties">
                        Year Range: 
                        <span v-if="typeof activePoint.properties.yr === 'string'">
                            {{ JSON.parse(activePoint.properties.yr)[0] }} - {{ JSON.parse(activePoint.properties.yr)[JSON.parse(activePoint.properties.yr).length - 1] }}
                        </span>
                        <span v-else>
                            {{ activePoint.properties.yr[0] }} - {{ activePoint.properties.yr[activePoint.properties.yr.length - 1] }}
                        </span>
                    </div>
                    <div v-if="'area' in activePoint.properties && activePoint.properties.area">
                        Area: {{ activePoint.properties.area.toFixed(1) }}
                    </div>
                    <div v-if="'status' in activePoint.properties">
                        Status: {{ activePoint.properties.status }}
                    </div>
                    <q-spinner 
                        v-if="loadingProperties"
                    />
                    <div v-if="'sampleDates' in activePoint.properties">
                        Sample Dates: {{ activePoint.properties.sampleDates }}
                    </div>
                    <div v-if="'uniqueParams' in activePoint.properties">
                        Unique Parameters: {{ activePoint.properties.uniqueParams }}
                    </div>
                </div>
                <div v-if="props.hasPropertyFilters">
                    <q-separator class="q-my-sm" />
                    Analysis metrics:
                    <template
                        v-for = "analysis in filters.other.analyses"
                        :key = "analysis.key"
                    >
                        <q-chip
                            v-if = "analysis.key in activePoint.properties && activePoint.properties[analysis.key]"
                            dense
                        >
                            {{ analysis.label }}
                        </q-chip>
                    </template>
                </div>
                <div>
                    <q-btn
                        v-if="props.viewMore"
                        class="q-mt-sm row"
                        label="View More"
                        color="primary"
                        @click="emit('view-more')"
                    />
                    <q-btn
                        v-if="activePoint && props.page !== 'watershed'"
                        class="q-mt-sm row"
                        label="Download Data"
                        color="primary"
                        @click="emit('download-data')"
                    />
                </div>
            </q-card>
            <div class="row justify-between">
                <h3>Filtered {{ props.title }}</h3>
                <q-btn icon="mdi-filter" flat>
                    <q-menu
                        v-if="props.map"
                        max-width="400px"
                    >
                        <div
                            v-if="localFilters.other"
                            class="filter-menu q-ma-md"
                        >
                            <div
                                v-for="(category, idx) in localFilters.other"
                                :key="idx"
                                class="flex column"
                            >
                                <h6 v-if="idx !== 'analyses'">
                                    {{ idx }}
                                </h6>
                                <h6 v-else>
                                    Analysis Metrics
                                </h6>
                                <q-checkbox
                                    v-for="button in category.sort((a, b) => a.label < b.label ? -1 : 1)"
                                    :key="button"
                                    v-model="button.value"
                                    :label="button.label"
                                    @update:model-value="emit('update-filter', localFilters)"
                                />
                            </div>
                        </div>
                        <div
                            v-if="props.hasFlowQuantity"
                            class="q-ma-md"
                        >
                            <h6>Quantity</h6>
                            <q-checkbox
                                v-for="(areaRange, idx) in flowRanges.quantity"
                                :key="idx"
                                v-model="areaRange.value"
                                :label="areaRange.label"
                                @update:model-value="() => {
                                    localFilters.quantity = flowRanges.quantity
                                    emit('update-filter', localFilters)
                                }"
                            />
                        </div>
                        <div
                            v-if="props.hasArea"
                            class="q-ma-md"
                        >
                            <h6>Area</h6>
                            <div class="filter-container">
                                <q-checkbox
                                    v-for="(areaRange, idx) in areaRanges.area"
                                    :key="idx"
                                    v-model="areaRange.value"
                                    :label="areaRange.label"
                                    @update:model-value="() => {
                                        localFilters.area = areaRanges.area
                                        emit('update-filter', localFilters)
                                    }"
                                />
                            </div>
                        </div>
                        <div
                            v-if="props.hasYearRange"
                            class="year-range q-ma-md"
                        >
                            <h6>Year Range</h6>
                            <q-input
                                v-model="startYear"
                                class="year-input q-mx-xs"
                                placeholder="Start Year"
                                mask="####"
                                dense
                                outlined
                                @update:model-value="() => {
                                    if(startYear && startYear.toString().length === 4){
                                        if(endYear && endYear.toString().length === 4){
                                            localFilters.year = [
                                                {
                                                    key: 'yr',
                                                    matches: startYear,
                                                    case: '>='
                                                },
                                                {
                                                    key: 'yr',
                                                    matches: endYear,
                                                    case: '<='
                                                },
                                            ]
                                        }
                                        emit('update-filter', localFilters)
                                    }
                                }"
                            />
                            <q-input
                                v-model="endYear"
                                class="year-input q-ml-xs"
                                placeholder="End Year"
                                mask="####"
                                dense
                                outlined
                                @update:model-value="() => {
                                    if(endYear && endYear.toString().length === 4){
                                        if(startYear && startYear.toString().length === 4){
                                            localFilters.year = [
                                                {
                                                    key: 'yr',
                                                    matches: startYear,
                                                    case: '>='
                                                },
                                                {
                                                    key: 'yr',
                                                    matches: endYear,
                                                    case: '<='
                                                },
                                            ]
                                        }
                                        emit('update-filter', localFilters)
                                    }
                                }"
                            />
                        </div>
                        <div class="reset-filters-container">
                            <q-btn
                                class="q-ma-md"
                                color="primary"
                                label="Reset filters"
                                @click="resetFilters"
                            />
                            <q-btn
                                class="q-ma-md"
                                color="primary"
                                label="Clear filters"
                                @click="clearFilters"
                            />

                        </div>
                    </q-menu>
                </q-btn>
            </div>
            <div class="map-point-count">
                <div v-if="props.page === 'watershed'">
                    <i>
                        {{ props.pointsToShow.length }} allocations {{ props.viewExtentOn ? '' : 'in view extent' }}
                    </i>
                </div>
                <div v-else>
                    <i>
                        {{ props.pointsToShow.length }} stations {{ props.viewExtentOn ? '' : 'in view extent' }}
                    </i>
                </div>

            </div>
            <q-input
                :model-value="textFilter"
                class="map-filter-search"
                label="Search"
                label-color="primary"
                clearable
                dense
                debounce="300"
                @update:model-value="updateTextFilter"
            />
        </div>

        <div
            v-if="props.loading"
            class="map-points-loader"
        >
            <q-spinner size="lg" />
            <div class="q-mt-sm">
                Getting points in map view...
            </div>
        </div>
        <!-- The max-height property of this to determine how much content to render in the virtual scroll -->
        <q-virtual-scroll
            class="map-points-list"
            :items="filteredPoints"
            v-slot="{ item, index }"
            style="max-height: 90%"
            separator
            :virtual-scroll-item-size="50"
            ref="virtualListRef"
        >
            <q-item
                :key="index"
                clickable
                @click="emit('select-point', item)"
            >
                <q-item-section avatar>
                    <q-avatar
                        color="grey-4"
                        :text-color="props.page === 'watershed' && item.properties.st === 'ACTIVE APPL.' ? 'warning' : 'primary'"
                        icon="mdi-map-marker"
                    />
                </q-item-section>
                <q-item-section>
                    <q-item-label
                        v-if="props.page === 'watershed'"
                    >
                        <span v-if="'lic' in item.properties">{{ item.properties.lic }}</span>
                    </q-item-label>
                    <q-item-label
                        v-if="props.page === 'watershed'"
                        class="item-label"
                    >
                        <div>
                            <span v-if="'org' in item.properties">
                                {{ item.properties.org }}
                            </span>
                            <span class="q-mx-sm">●</span>
                            <span v-if="'qty' in item.properties && item.properties.qty > 0">
                                {{ item.properties.qty }} m<sup>3</sup>/year
                            </span>
                        </div>
                        <div v-if="'src_name' in item.properties">
                            Source: {{ item.properties.src_name }}
                        </div>
                        <div>
                            Licence: <span v-if="'id' in item.properties">({{ item.properties.nid }})</span>
                        </div>
                    </q-item-label>
                    <div v-else>
                        <q-item-label v-if="'name' in item.properties">
                            {{ item.properties.name }}
                        </q-item-label>
                        <q-item-label v-if="'id' in item.properties" class="item-label">
                            ID: {{ item.properties.id }}
                        </q-item-label>
                        <q-item-label v-if="'area' in item.properties && item.properties.area" class="item-label">
                            Area: {{ item.properties.area }}
                        </q-item-label>
                        <q-item-label v-if="'type' in item.properties" class="item-label">
                            Type: {{ item.properties.type }}
                        </q-item-label>
                         <template
                            v-for='analysis in filters.other.analyses'
                            :key = "analysis.key"
                         >
                            <q-chip
                            v-if="analysis.key in item.properties && item.properties[analysis.key]"
                                dense
                            >
                                {{ analysis.label }}
                            </q-chip>
                        </template>
                    </div>
                </q-item-section>
            </q-item>
        </q-virtual-scroll>
    </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { getSurfaceWaterStationStatistics, getGroundWaterStationStatistics } from '@/utils/api.js';

const props = defineProps({
    allPoints: {
        type: Object,
        default: () => {},
    },
    loading: {
        type: Boolean,
        default: false,
    },
    title: {
        type: String,
        default: "",
    },
    paragraph: {
        type: String,
        default: "",
    },
    page: {
        type: String,
        default: "",
    },
    filters: {
        type: Object,
        default: () => {},
    },
    selectedPointFromMap: {
        type: Object,
        default: () => {},
    },
    pointsToShow: {
        type: Object,
        default: () => {},
    },
    totalPointCount: {
        type: Number,
        default: 0,
    },
    map: {
        type: Object || null,
        default: null,
    },
    viewMore: {
        type: Boolean,
        default: true,
    },
    hasFlowQuantity: {
        type: Boolean,
        default: false,
    },
    hasYearRange: {
        type: Boolean,
        default: false,
    },
    hasArea: {
        type: Boolean,
        default: false,
    },
    hasPropertyFilters: {
        type: Boolean,
        default: false
    },
    viewExtentOn: {
        type: Boolean,
        default: false
    },
});

const emit = defineEmits(["download-data", "update-filter", "select-point", "view-more"]);
const virtualListRef = ref(null);
const localFilters = ref({});
const textFilter = ref("");
const startYear = ref();
const endYear = ref();
const loadingProperties = ref(false);
const activePoint = ref();
const areaRanges = ref({
    area: [
        { label: "5 km² or less", high: 5, value: true },
        { label: "50 km² or less", high: 50, value: true },
        { label: "50 km² – 100 km²", low: 50, high: 100, value: true },
        { label: "100 km² – 200 km²", low: 100, high: 200, value: true },
        { label: "200 km² – 300 km²", low: 200, high: 300, value: true },
        { label: "300 km² – 500 km²", low: 300, high: 500, value: true },
        { label: "500 km² – 1,000 km²", low: 500, high: 1000, value: true },
        { label: "1,000 km² – 2,500 km²", low: 1000, high: 2500, value: true },
        { label: "2,500 km² – 5,000 km²", low: 2500, high: 5000, value: true },
        { label: "5,000 km² – 10,000 km²", low: 5000, high: 10000, value: true },
        { label: "10,000 km² – 25,000 km²", low: 10000, high: 25000, value: true },
        { label: "25,000 km² – 50,000 km²", low: 25000, high: 50000, value: true },
        { label: "50,000 km² or more", low: 50000, value: true },
        { label: "100,000 km² or more", low: 100000, value: true }
    ]
});
const flowRanges = ref({
    quantity: [
        { label: '10,000 m³/year or less', value: true, },
        { label: '10,000 m³/year – 50,000 m³/year', value: true, low: 10000, high: 50000 },
        { label: '50,000 m³/year – 100,000 m³/year', value: true, low: 50000, high: 100000 },
        { label: '100,000 m³/year – 500,000 m³/year', value: true, low: 100000, high: 500000 },
        { label: '500,000 m³/year – 1,000,000 m³/year', value: true, low: 500000, high: 1000000 },
        { label: '1,000,000 m³/year or more', value: true, }
    ]
});

watch(() => props.allPoints, (newval) => {
    setFilterOptions(newval.features);
});

watch(() => props.selectedPointFromMap, async (newval) => {
    activePoint.value = newval;
    if (!activePoint.value) return;

    if (props.title === 'Water Quality Stations') {
        loadingProperties.value = true;
        const response = await getSurfaceWaterStationStatistics(activePoint.value.properties.id);
        if('sampleDates' in response) activePoint.value.properties.sampleDates = response.sampleDates;
        if('uniqueParams' in response) activePoint.value.properties.uniqueParams = response.uniqueParams;
        loadingProperties.value = false;
    }
    else if (props.title === 'Ground Water Quality') {
        loadingProperties.value = true;
        const response = await getGroundWaterStationStatistics(activePoint.value.properties.id);
        if('sampleDates' in response) activePoint.value.properties.sampleDates = response.sampleDates;
        if('uniqueParams' in response) activePoint.value.properties.uniqueParams = response.uniqueParams;
        loadingProperties.value = false;
    }
});

onMounted(() => {
    localFilters.value = props.filters;
    if (props.hasArea) {
        localFilters.value.area = areaRanges.value.area;
    }
    if (props.hasFlowQuantity) {
        localFilters.value.quantity = flowRanges.value.quantity;
    }
});

const setFilterOptions = (points) => {
    const uniqueNetworks = [];
    
    points.forEach(feature => {
        if(!uniqueNetworks.includes(feature.properties.net)){
            uniqueNetworks.push(feature.properties.net);
        }
    })

    localFilters.value.other.network = uniqueNetworks.map(el => {
        return {
            value: true,
            label: el,
            key: 'net',
            matches: el
        }
    });
}

const updateTextFilter = (text) => {
    textFilter.value = text === null ? "" : text;
}

const filteredPoints = computed(() => {
    return props.pointsToShow.filter((point) => {
        return (
            point.properties.id.toString().toLowerCase().includes(textFilter.value.toLowerCase()) ||
            ('name' in point.properties && point.properties.name.toString().toLowerCase().includes(textFilter.value.toLowerCase())) ||
            ('nid' in point.properties && point.properties.name.toString().toLowerCase().includes(textFilter.value.toLowerCase()))
        )
    });
});

const resetFilters = () => {
    Object.keys(localFilters.value).forEach(el => {
        if(el === 'other'){
            for(const filter in localFilters.value[el]){
                localFilters.value[el][filter].forEach(toggle => {
                    toggle.value = true;
                });
            }
        }
        if(el === 'year'){
            localFilters.value[el].start = null;
            localFilters.value[el].end = null;
        }
        if(el === 'quantity' || el === 'area'){
            localFilters.value[el].forEach(filter => {
                filter.value = true;
            })
        }
    });
    emit('update-filter', localFilters.value);
};

const clearFilters = () => {
    Object.keys(localFilters.value).forEach(el => {
        if(el === 'other'){
            for(const filter in localFilters.value[el]){
                localFilters.value[el][filter].forEach(toggle => {
                    toggle.value = false;
                });
            }
        }
        if(el === 'year'){
            localFilters.value[el].start = null;
            localFilters.value[el].end = null;
        }
        if(el === 'quantity' || el === 'area'){
            localFilters.value[el].forEach(filter => {
                filter.value = false;
            })
        }
    });
    emit('update-filter', localFilters.value);
};


/**
 * Check if a station has a module by comparing its analysis keys against the required keys for said module
 * @param {*} array1 station analysis object keys
 * @param {*} array2 keys that indicate a module is available
 */
const stationHasModule = (array1, array2) => {
    let hasMatch = false;
    array1.forEach(el => {
        if (array2.includes(el)) hasMatch = true;
    });
    return hasMatch;
};
</script>

<style lang="scss" scoped>
.map-points-list {
    max-height: 100%;
    overflow-y: auto;
}

.map-points-loader {
    display: flex;
    flex-direction: column;
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(255, 255, 255, 0.5);
    z-index: 1;
    align-items: center;
    justify-content: center;
}

.map-filters-container {
    background-color: white;
    color: black;
    display: flex;
    position: relative;
    flex-direction: column;
    width: 30vw;
    height: 100vh;

    .map-filters-header {
        font-family: 'BC Sans', sans-serif;
        font-size: 20pt;
        font-weight: bold;
        margin: 1rem 0;
    }
}

.filter-menu {
    background-color: white;
    color: black;
}

.selected-point {
    border: 1px solid black;
    border-radius: 0.3em;
    padding: 0.5em;
}

.filter-container {
    display: flex;
    flex-direction: column;
}

.active-point {
    background-color: $light-grey-accent;
}

.station-container {
    cursor: pointer;

    &:hover {
        background-color: grey;
    }
}

.item-label {
    font-size: 10pt;
    color: #606060;
}

.year-range {
    display: flex;
    align-items: center;

    .year-input {
        width: 8rem;
    }
}

h6 {
    text-transform: capitalize;
    margin: 0;
}
</style>
