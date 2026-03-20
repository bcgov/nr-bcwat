<template>
    <div class="map-filters-container">
        <div class="q-pa-sm">
            <div class="map-filters-header text-h4">
                {{ props.title }}
            </div>
            <p>{{ props.paragraph }}</p>
            <q-card
                v-if="activePoint?.properties && Object.keys(activePoint.properties).length"
                class="selected-point q-pa-sm q-ma-sm"
                flat
                bordered
            >
                <!-- Watershed active point structure -->
                <q-item v-if="props.page === 'watershed'">
                    <q-item-section>
                        <div
                            v-if="'lic' in activePoint.properties"
                            class="text-h6 point-title"
                        >
                            <div class="point-title-text">
                                {{ activePoint.properties.lic }}<span v-if="!activePoint.properties.lic">No Name</span><span v-if="'nid' in activePoint.properties">, {{ activePoint.properties.nid }}</span>
                            </div>
                            <div>
                                <q-btn
                                    round
                                    flat
                                    icon="location_on"
                                    @click="goToLocation(activePoint, props.map)"
                                >
                                    <q-tooltip>Go to location</q-tooltip>
                                </q-btn>
                            </div>
                        </div>
                        <div v-if="'pod' in activePoint.properties">
                            POD: {{ activePoint.properties.pod }}
                        </div>
                        <div v-if="'qty' in activePoint.properties">
                            Quantity: {{ activePoint.properties.qty }} m³/year
                        </div>
                        <div v-if="'purpose' in activePoint.properties">
                            Licence Purpose: {{ activePoint.properties.purpose }}
                        </div>
                        <div v-if="'term' in activePoint.properties">
                            Term: {{ activePoint.properties.term }}
                        </div>
                        <div v-if="'st' in activePoint.properties">
                            Status: {{ activePoint.properties.st }}
                        </div>
                    </q-item-section>
                </q-item>
                <!-- Groundwater active point structure -->
                <q-item v-if="props.page === 'groundwater'">
                    <q-item-section avatar>
                        <q-avatar color="grey-4" text-color="'orange'" icon="mdi-map-marker"/>
                    </q-item-section>
                    <q-item-section>
                        <div v-if="'id' in activePoint.properties">
                            ID: {{ activePoint.properties.id }}
                        </div>
                        <div v-if="'well_tag_number' in activePoint.properties">
                            Well Tag Number: {{ activePoint.properties.well_tag_number }}
                        </div>
                        <div v-if="'well_tag_number' in activePoint.properties">
                            Use Code: {{ activePoint.properties.use_code }}
                        </div>
                        <div>
                            Well Details: <a :href="activePoint.properties.details_url" target="_blank">{{ activePoint.properties.details_url }}</a>
                        </div>
                    </q-item-section>
                </q-item>
                <!-- cda active point structure -->
                <q-item v-if="props.page === 'cda'">
                    <q-item-section avatar>
                        <q-avatar color="grey-4" :text-color="activePoint.properties.type === 'SW' ? 'green-6' : 'indigo-9'" icon="mdi-map-marker"/>
                    </q-item-section>
                    <q-item-section>
                        <div v-if="'id' in activePoint.properties">
                            ID: {{ activePoint.properties.id }}
                        </div>
                        <div v-if="'ind' in activePoint.properties">
                            Industry: {{ activePoint.properties.ind }}
                        </div>
                        <div v-if="'st' in activePoint.properties">
                            Status: {{ activePoint.properties.st }}
                        </div>
                        <div v-if="'qty' in activePoint.properties">
                            Quantity: {{ activePoint.properties.qty }} m³/year
                        </div>
                    </q-item-section>
                </q-item>
                <!-- Water portal page active point structure -->
                <q-item v-if="props.page === 'water-portal' && activePoint">
                    <q-item-section avatar>
                        <q-avatar color="grey-4" :text-color="activePoint.properties.status.includes('Active') ? 'warning' : 'positive'" icon="mdi-map-marker"/>
                    </q-item-section>
                    <q-item-section>
                        <div
                            v-if="'name' in activePoint.properties"
                            class="text-h6"
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
                            Year Range: {{ activePoint.properties.yr[0] }} - {{ activePoint.properties.yr[activePoint.properties.yr.length - 1] }}
                        </div>
                        <div v-if="'term' in activePoint.properties">
                            Term: {{ activePoint.properties.term }}
                        </div>
                        <div v-if="'status' in activePoint.properties">
                            Status: {{ activePoint.properties.status }}
                        </div>
                    </q-item-section>
                </q-item>
                <div v-if="props.hasPropertyFilters">
                    <q-separator class="q-my-sm" />
                    Analysis metrics:
                    <template
                        v-for = "analysis in filters.other.analyses"
                    >
                        <q-chip
                            v-if = "analysis.key in activePoint.properties && activePoint.properties[analysis.key]"
                            :key = "analysis.key"
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
                        v-if="activePoint && props.downloadable"
                        class="q-mt-sm row"
                        label="Download Data"
                        color="primary"
                        @click="emit('download-data')"
                    />
                </div>
            </q-card>

            <div v-if="props.page === 'watershed' || props.page === 'cda'" class="watershed-legend">
                <q-card
                    v-if="localFilters && 'matchFilters' in localFilters"
                    class="legend-contents q-pa-sm"
                    flat
                >
                    <div
                        v-for="button in localFilters.matchFilters.find(cat => cat.category === 'Type').filters"
                        :key="button.label"
                        class="legend-item"
                    >
                        <div class="legend-point">
                            <span
                                class="dot"
                                :class="button.matchValue"
                            />
                            {{ button.label }}
                        </div>
                        <q-toggle
                            :key="button"
                            v-model="button.model"
                            @update:model-value="emit('update-filter', localFilters)"
                        />
                    </div>
                    <div
                        v-if="localFilters.matchFilters[0].filters.find(el => el.property)"
                        class="legend-item"
                    >
                        <div class="legend-point">
                            <span class="dot active" />
                            Active Application
                        </div>
                        <div>
                            <q-toggle
                                v-model="localFilters.matchFilters[4].filters.find(el => el.matchValue === 'ACTIVE APPL.').model"
                                @update:model-value="() => {
                                    emit('update-filter', localFilters)
                                }"
                            />
                        </div>
                    </div>
                </q-card>
            </div>

            <div class="row justify-between points-label-row">
                <div class="text-h5 q-my-md">{{ props.shapeUsed ? 'Selected ' : '' }}{{ props.pointsName }}</div>
                <div>
                    <q-btn
                        v-if="props.page !== 'groundwater'"
                        icon="mdi-filter"
                        round
                        flat
                    >
                        <q-menu
                            v-if="props.map"
                            max-width="400px"
                        >
                            <div
                                v-if="localFilters.matchFilters"
                                class="filter-menu q-ma-md"
                            >
                                <div
                                    v-for="(category, idx) in localFilters.matchFilters"
                                    :key="idx"
                                    class="flex column"
                                >

                                    <h6>
                                        {{ category.category }}
                                    </h6>
                                    <q-checkbox
                                        v-for="filter in category.filters"
                                        :key="filter"
                                        v-model="filter.model"
                                        :label="filter.label"
                                        @update:model-value="emit('update-filter', localFilters)"
                                    />
                                </div>
                            </div>
                            <div
                                v-if="props.filterableProperties?.uniqueFilters?.hasQuantity"
                                class="q-ma-md"
                            >
                                <h6>Quantity</h6>
                                <q-checkbox
                                    v-for="(quantityRange, idx) in localFilters.uniqueFilters.quantity"
                                    :key="idx"
                                    v-model="quantityRange.value"
                                    :label="quantityRange.label"
                                    @update:model-value="() => {
                                        emit('update-filter', localFilters)
                                    }"
                                />
                            </div>
                            <div
                                v-if="props.filterableProperties?.uniqueFilters?.hasArea"
                                class="q-ma-md"
                            >
                                <h6>Area</h6>
                                <div class="filter-container">
                                <q-checkbox
                                    v-for="(areaRange, idx) in localFilters.uniqueFilters.areaRange"
                                    :key="idx"
                                    v-model="areaRange.value"
                                    :label="areaRange.label"
                                    @update:model-value="() => {
                                        emit('update-filter', localFilters)
                                    }"
                                />
                                </div>
                            </div>
                            <div
                                v-if="props.filterableProperties?.uniqueFilters?.hasYearRange"
                                class="year-range q-ma-md"
                            >
                                <h6>Year Range</h6>
                                <div class="year-input-container">
                                    <q-input
                                        :model-value="localFilters.uniqueFilters.yearRange.min"
                                        class="year-input q-mx-xs"
                                        placeholder="Start Year"
                                        dense
                                        outlined
                                        @update:model-value="(newval) => {
                                            localFilters.uniqueFilters.yearRange.min = newval;
                                            if (newval && newval.toString().length === 4) {
                                                if (newval && newval.toString().length === 4) {
                                                    emit('update-filter', localFilters)
                                                }
                                            }
                                        }"
                                    />
                                    <q-input
                                        :model-value="localFilters.uniqueFilters.yearRange.max"
                                        class="year-input q-ml-xs"
                                        placeholder="End Year"
                                        dense
                                        outlined
                                        @update:model-value="(newval) => {
                                            localFilters.uniqueFilters.yearRange.max = newval;
                                            if (newval && newval.toString().length === 4) {
                                                emit('update-filter', localFilters)
                                            }
                                        }"
                                    />
                                </div>
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
            </div>
            <div class="map-point-count">
                <div>
                    <i>
                        {{ props.pointsToShow ? props.pointsToShow.length : '0' }}
                        <span>{{props.pointsToShow?.length === 1 ? 'location' : 'locations'}} {{ props.shapeUsed ? 'selected by polygon' : 'in view extent' }}</span>
                    </i>
                </div>
            </div>
            <q-input
                v-model="textFilter"
                class="map-filter-search"
                label="Search"
                label-color="primary"
                clearable
                dense
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
        <div
            v-if="filteredPoints && !filteredPoints.length"
            class="q-ma-md"
        >
            <div class="text-h6">
                No results.
            </div>
            <div v-if="textFilter?.length">
                You have a search filter applied that may be too restrictive.
            </div>
            There may be no {{ props.pointsName.toLowerCase() }} in the current map view.
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
                @click="() => {
                    emit('select-point', item)
                    selectPoint(item)
                }"
            >
                <q-item-section
                    v-if="props.page === 'water-portal'"
                    avatar
                >
                    <q-avatar color="grey-4" :text-color="item.properties.status.includes('Active') ? 'warning' : 'positive'" icon="mdi-map-marker"/>
                </q-item-section>
                <q-item-section
                    v-if="props.page === 'watershed' || props.page === 'cda'"
                    avatar
                >
                    <q-avatar
                        color="grey-4"
                        :text-color="item.properties.type === 'SW' ? 'green-6' : 'indigo-9'"
                        icon="mdi-map-marker"
                    />
                </q-item-section>
                <q-item-section>
                    <div v-if="props.page === 'watershed'">
                        <q-item-label>
                            <span v-if="'lic' in item.properties">{{ item.properties.lic }}</span>
                        </q-item-label>
                        <q-item-label
                            class="item-label"
                        >
                            <div v-if="'org' in item.properties">
                                {{ item.properties.org }}
                            </div>
                            <div v-if="'qty' in item.properties && item.properties.qty > 0">
                                Quantity: {{ item.properties.qty }} m³/year
                            </div>
                            <div v-if="'src_name' in item.properties">
                                Source: {{ item.properties.src_name }}
                            </div>
                            <div v-if="'nid' in item.properties">
                                Licence: <span>({{ item.properties.nid }})</span>
                            </div>
                            <div v-if="'pod' in item.properties">
                                POD: {{ item.properties.pod }}
                            </div>
                        </q-item-label>
                    </div>
                    <div v-if="props.page === 'cda'">
                        <q-item-label>
                            <span v-if="'lic' in item.properties">{{ item.properties.lic }}</span>
                        </q-item-label>
                        <q-item-label
                            class="item-label"
                        >
                            <div>
                                <span v-if="'org' in item.properties">{{ item.properties.org }}</span>
                                <q-icon v-if="'org' in item.properties" name="mdi-circle-small" size="sm" />
                                <span v-if="'qty' in item.properties && item.properties.qty > 0">{{ item.properties.qty }} m³/year</span>
                            </div>
                            <div v-if="'nid' in item.properties">
                                Licence: <span>({{ item.properties.nid }})</span>
                            </div>
                        </q-item-label>
                    </div>
                    <!-- listing contents specifically for groundwater page -->
                    <div v-else-if="props.page === 'groundwater'">
                        <q-item-label v-if="'id' in item.properties">
                            ID: {{ item.properties.id }}
                        </q-item-label>
                        <q-item-label v-if="'well_tag_number' in item.properties" class="item-label">
                            Well Tag Number: {{ item.properties.well_tag_number }}
                        </q-item-label>
                    </div>
                    <!-- listing contents specifically for water portal page -->
                    <div v-else-if="props.page === 'water-portal'">
                        <q-item-label v-if="'name' in item.properties">
                            Station: {{ item.properties.name }}
                        </q-item-label>
                        <q-item-label v-if="'yr' in item.properties" class="item-label">
                            Year Range: {{ yearRangeString(item.properties.yr) }}
                        </q-item-label>
                        <q-item-label v-if="'area' in item.properties" class="item-label">
                            Area: {{ item.properties.area }}km²
                        </q-item-label>
                        <q-item-label v-if="'net' in item.properties" class="item-label">
                            Network: {{ item.properties.net }}
                        </q-item-label>
                        <!-- handling for "analysesObj" display -->
                        <div v-if="props.filterableProperties && Object.keys(props.filterableProperties).length && props.filterableProperties.matchFilters.find(el => el.category === 'Analysis Metrics')">
                            <template
                                v-for="analysis in props.filterableProperties.matchFilters.find(el => el.category === 'Analysis Metrics').filters"
                                :key = "analysis"
                            >
                                <q-chip
                                    v-if="analysis in item.properties && item.properties[analysis.key]"
                                    dense
                                >
                                    {{ analysis.label }}
                                </q-chip>
                            </template>
                        </div>
                    </div>
                </q-item-section>
            </q-item>
        </q-virtual-scroll>
    </div>
</template>

<script setup>
import { goToLocation } from '@/utils/mapHelpers.js';
import { computed, ref, watch } from "vue";
import { yearRangeString } from "@/utils/stringHelpers.js";

const props = defineProps({
    allPoints: {
        type: Object,
        default: () => {},
    },
    downloadable: {
        type: Boolean,
        default: false
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
    pointsName: {
        type: String,
        default: "",
    },
    selectedPointFromMap: {
        type: Object,
        default: () => {},
    },
    shapeUsed: {
        type: Boolean,
        default: false
    },
    pointsToShow: {
        type: Object,
        default: () => {},
        required: true,
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
    filterableProperties: {
        type: Object,
        default: () => {},
        required: true,
    },
});

const emit = defineEmits(["download-data", "update-filter", "select-point", "view-more"]);

const yearRangeDefault = ref();
const areaRangeDefaults = [
    { label: "5 km² or less", low: 0, high: 5, value: true },
    { label: "5 km² – 50 km²", low: 5, high: 50, value: true },
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
    { label: "50,000 km² – 100,000 km²", low: 50000, high: 100000, value: true },
    { label: "100,000 km² or more", low: 100000, high: Infinity, value: true }
];
const flowRangeDefault = [
    { label: '10,000 m³/year or less', value: true, low: 0, high: 10000 },
    { label: '10,000 m³/year - 50,000 m³/year', value: true, low: 10000, high: 50000 },
    { label: '50,000 m³/year - 100,000 m³/year', value: true, low: 50000, high: 100000 },
    { label: '100,000 m³/year - 500,000 m³/year', value: true, low: 100000, high: 500000 },
    { label: '500,000 m³/year - 1,000,000 m³/year', value: true, low: 500000, high: 1000000 },
    { label: '1,000,000 m³/year or more', value: true, low: 1000000, high: Infinity },
];

const activePoint = ref();
const localFilters = ref({});
const textFilter = ref("");

watch(() => props.selectedPointFromMap, (newval) => {
    activePoint.value = newval;
});

watch(() => props.filterableProperties, () => {
    if (!props.filterableProperties || !('matchFilters' in props.filterableProperties) && !('uniqueFilters' in props.filterableProperties)) return;
    localFilters.value = props.filterableProperties;

    // add a toggle-able model for the matching-type boolean filters
    localFilters.value.matchFilters.forEach(category => {
        category.filters.forEach(filter => {
            filter.model = true;
        });
    })

    if (props.filterableProperties.uniqueFilters.hasArea) {
        localFilters.value.uniqueFilters.areaRange = JSON.parse(JSON.stringify(areaRangeDefaults));
    }
    if (props.filterableProperties.uniqueFilters.hasQuantity) {
        localFilters.value.uniqueFilters.quantity = JSON.parse(JSON.stringify(flowRangeDefault));
    }
    if (props.filterableProperties.uniqueFilters.hasYearRange) {
        yearRangeDefault.value = JSON.parse(JSON.stringify(props.filterableProperties.uniqueFilters.yearRange));
    }
});

const selectPoint = (item) => {
    activePoint.value = item;
}

// search term filtering in sidebar
const filteredPoints = computed(() => {
    if (textFilter.value === '' || textFilter.value === null) return props.pointsToShow;
    return props.pointsToShow.filter((point) => {
        if (props.page === 'water-portal') {
            return (
                point.properties.id.toString().includes(textFilter.value) ||
                ('net' in point.properties && point.properties.net.toString().toLowerCase().includes(textFilter.value.toLowerCase())) ||
                ('area' in point.properties && point.properties.area !== null && point.properties.area.toString().toLowerCase().includes(textFilter.value.toLowerCase())) ||
                ('name' in point.properties && point.properties.name.toString().toLowerCase().includes(textFilter.value.toLowerCase()))
            )
        }
        if (props.page === 'groundwater') {
            return (
                ('id' in point.properties && point.properties.id.toString().toLowerCase().includes(textFilter.value.toLowerCase())) ||
                ('well_tag_no' in point.properties && point.properties.well_tag_no.toString().toLowerCase().includes(textFilter.value.toLowerCase()))
            )
        }
        if (props.page === 'watershed') {
            return (
                point.properties.id.toString().includes(textFilter.value) ||
                ('lic' in point.properties && point.properties.lic.toString().toLowerCase().includes(textFilter.value.toLowerCase())) ||
                ('nid' in point.properties && point.properties.nid.toString().toLowerCase().includes(textFilter.value.toLowerCase())) ||
                ('src_name' in point.properties && point.properties.src_name.toString().toLowerCase().includes(textFilter.value.toLowerCase())) ||
                ('pod' in point.properties && point.properties.pod.toString().toLowerCase().includes(textFilter.value.toLowerCase())) ||
                ('org' in point.properties && point.properties.org.toString().toLowerCase().includes(textFilter.value.toLowerCase()))
            )
        }
    });
});

const resetFilters = () => {
    if (!Object.keys(localFilters.value).length) return;
    localFilters.value.matchFilters.forEach(category => {
        category.filters.forEach(filter => {
            filter.model = true;
        });
    });

    // special handling for the uniqueFilters categories
    if (localFilters.value.uniqueFilters.hasArea) {
        localFilters.value.uniqueFilters.areaRange = areaRangeDefaults;
    }
    if (localFilters.value.uniqueFilters.hasQuantity) {
        localFilters.value.uniqueFilters.quantity.forEach(el => {
            el.value = true;
        })
    }
    if (localFilters.value.uniqueFilters.hasYearRange) {
        localFilters.value.uniqueFilters.yearRange = yearRangeDefault.value;
    }

    emit('update-filter', localFilters.value);
};

const clearFilters = () => {
    if (!Object.keys(localFilters.value).length) return;
    localFilters.value.matchFilters.forEach(category => {
        category.filters.forEach(filter => {
            filter.model = false;
        });
    });
    if (localFilters.value.uniqueFilters.hasQuantity) {
        localFilters.value.uniqueFilters.quantity.forEach(el => {
            el.value = false;
        });
    }
    if (localFilters.value.uniqueFilters.hasArea) {
        localFilters.value.uniqueFilters.areaRange = areaRangeDefaults;
    }
    if (localFilters.value.uniqueFilters.hasYearRange) {
        localFilters.value.uniqueFilters.yearRange = {
            min: '',
            max: ''
        };
    }

    emit('update-filter', localFilters.value);
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
    height: 100vh;

    .marker-labels {
        display: flex;
        align-items: center;
        justify-content: space-around;
    }

    .map-filters-header {
        margin: 1rem 0;
    }

    .main-filter-section {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        grid-template-rows: 1fr;

        .main-filter-section-btns {
            display: flex;
            flex-direction: column;
        }
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

    .q-item {
        word-wrap: break-word;
        line-break: anywhere;
    }
}

.filter-container {
    display: flex;
    flex-direction: column;
}

.points-label-row {
    display: flex;
    align-items: center;
}

.watershed-legend {
    display: grid;
    grid-template-columns: 1fr 1fr;
    position: absolute;
    top: 0.2rem;
    left: calc(100% + 0.3rem);
    z-index: 1;

    .legend-contents {
        background-color: rgba(255, 255, 255, 0.8);
        transition-duration: 0.2s;
        width: 16rem;

        &:hover {
            background-color: rgba(255, 255, 255);
        }

        .legend-item {
            display: flex;
            justify-content: space-between;

            .legend-point {
                display: flex;
                align-items: center;

                .dot {
                    height: 1rem;
                    width: 1rem;
                    border: 2px solid black;
                    border-radius: 50%;
                    margin-right: 1rem;

                    &.GW {
                        background-color: #234075;
                        border-color: white;
                    }
                    &.SW {
                        background-color: #61913D;
                        border-color: white;
                    }
                    &.active {
                        border-color: goldenrod;
                    }
                }
            }
        }
    }
}

.active-point {
    background-color: $light-grey-accent;
}

.point-title {
    display: flex;
    justify-content: space-between;

    .point-title-text {
        word-break: initial;
    }
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
    flex-direction: column;

    .year-input-container {
        display: flex;

        .year-input {
            width: 8rem;
        }
    }
}

h6 {
    text-transform: capitalize;
    margin: 0;
}
</style>
