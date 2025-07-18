<template>
    <div class="map-filters-container">
        <div class="q-pa-sm">
            <div v-if="localFilters.buttons">
                <h1>{{ props.title }}</h1>
                <q-checkbox
                    v-for="button in localFilters.buttons"
                    :key="button"
                    v-model="button.value"
                    :label="button.label"
                    :color="button.color"
                    @update:model-value="emit('update-filter', localFilters)"
                />
            </div>
            <q-card v-if="activePoint" class="q-pa-sm q-ma-sm" flat bordered>
                <pre>{{ activePoint.properties.nid }}</pre>
                <div v-if="'name' in activePoint.properties">
                    Name: {{ activePoint.properties.name }}
                </div>
                <div>
                    ID: {{ activePoint.properties.id }}
                </div>
                <div>
                    NID: {{ activePoint.properties.nid }}
                </div>
                <div v-if="'net' in activePoint.properties">
                    Network: {{ activePoint.properties.net }}
                </div>
                <div v-if="'status' in activePoint.properties">
                    Status: 
                    <q-chip
                        :color="computedStatusColor"
                        dense
                    >
                        {{ activePoint.properties.status }}
                    </q-chip>
                </div>
                <div v-if="'qty' in activePoint.properties">
                    Quantity: {{ activePoint.properties.qty }} m<sup>3</sup>/year
                </div>
                <div v-if="'area' in activePoint.properties">
                    Drainage Area: {{ activePoint.properties.area }} km<sup>2</sup>
                </div>
                <div v-if="'st' in activePoint.properties">
                    Status: 
                    <q-chip
                        :color="computedStatusColor"
                        dense
                    >
                        {{ activePoint.properties.st }}
                    </q-chip>
                </div>
                <div v-if="'term' in activePoint.properties">
                    Term: {{ activePoint.properties.term }}
                </div>
                <div v-if="'yr' in activePoint.properties">
                    Year Range: {{ JSON.parse(activePoint.properties.yr)[0] }} - {{ JSON.parse(activePoint.properties.yr)[JSON.parse(activePoint.properties.yr).length - 1] }}
                </div>
                <div v-if="'analysesObj' in activePoint.properties && Object.keys(JSON.parse(activePoint.properties.analysesObj)).length > 0">
                    <q-separator class="q-my-sm" />
                    Analysis metrics: 
                    <q-chip 
                        v-for="obj in Object.keys(JSON.parse(activePoint.properties.analysesObj))"
                        :key="obj"
                        dense
                    >
                        {{ analysesObjMapping.find(el => `${el.id}` === `${obj}`).label }}
                    </q-chip>
                </div>
                <q-btn
                    v-if="props.viewMore"
                    class="q-mt-sm"
                    label="View More"
                    color="primary"
                    @click="emit('view-more')"
                />
            </q-card>
            <div class="row justify-between">
                <h3>Filtered {{ props.title }}</h3>
                <q-btn icon="mdi-filter" flat>
                    <q-menu
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
                                <h6>
                                    {{ idx }}
                                </h6>
                                <q-checkbox
                                    v-for="button in category"
                                    :key="button"
                                    v-model="button.value"
                                    :label="button.label"
                                    @update:model-value="
                                        emit('update-filter', localFilters)
                                    "
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
                            <q-input
                                v-model="startYear"
                                class="year-input q-mr-xs"
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
                        <div 
                            v-if="'analysesObj' in activePoint.properties"
                            class="q-ma-md"
                        >
                            <h6>Analyses</h6>
                            <q-checkbox
                                v-for="item in analysesObj"
                                v-model="item.value"
                                :key="item"
                                :label="item.label"
                                @update:model-value="() => {
                                    localFilters.analysesObj = analysesObj
                                    emit('update-filter', localFilters)
                                }"
                            />
                        </div>
                        <div class="reset-filters-container q-ma-md">
                            <q-btn
                                color="primary"
                                label="Reset filters"
                                @click="resetFilters"
                            />
                        </div>
                    </q-menu>
                </q-btn>
            </div>
            <div class="map-point-count">
                <i>{{ props.pointsToShow.length }} Stations in Map Range</i>
            </div>
            <q-input
                v-model="textFilter"
                class="map-filter-search"
                label="Search"
                label-color="primary"
                clearable
                dense
                debounce="300"
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
                @click="emit('select-point', item.properties)"
            >
                <q-item-section>
                    <q-item-label>
                        Allocation ID: {{ item.properties.nid }}
                    </q-item-label>
                    <q-item-label v-if="'name' in item.properties">
                        Name: {{ item.properties.name }}
                    </q-item-label>
                    <q-item-label class="item-label" caption>
                        ID: {{ item.properties.id }}
                    </q-item-label>
                    <q-item-label class="item-label" caption>
                        Net: {{ item.properties.net }}
                    </q-item-label>
                    <q-item-label class="item-label" caption>
                        Type: {{ item.properties.type }}
                    </q-item-label>
                </q-item-section>
            </q-item>
        </q-virtual-scroll>
    </div>
</template>

<script setup>
import { analysesObjMapping } from '@/constants/analysesMapping.js';
import { computed, onBeforeUnmount, onMounted, ref } from "vue";

const props = defineProps({
    loading: {
        type: Boolean,
        default: false,
    },
    title: {
        type: String,
        default: "",
    },
    filters: {
        type: Object,
        default: () => {},
    },
    activePointId: {
        type: String || Number,
        default: "",
    },
    pointsToShow: {
        type: Object,
        default: () => {},
    },
    totalPointCount: {
        type: Number,
        default: 0,
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
    }
});

const emit = defineEmits(["update-filter", "select-point", "view-more"]);
const virtualListRef = ref(null);
const localFilters = ref({});
const textFilter = ref("");
const startYear = ref();
const endYear = ref();
const analysesObj = ref(analysesObjMapping);
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
        { label: '1,000,000 m³/year or more', value: true, },
    ]
});

onMounted(() => {
    localFilters.value = props.filters;
});

onBeforeUnmount(() => {
    resetFilters();
});

const computedStatusColor = computed(() => {
    if(activePoint.value && 'status' in activePoint.value.properties){
        if(activePoint.value.properties.status.includes('Active')){
            return 'orange';
        }
        if(activePoint.value.properties.status === 'Historical'){
            return 'blue';
        }
    }
    if(activePoint.value && 'st' in activePoint.value.properties){
        if(activePoint.value.properties.st === 'CURRENT'){
            return 'orange';
        }
        if(activePoint.value.properties.st.includes('ACTIVE APPL.')){
            return 'blue';
        }
    }
});

const activePoint = computed(() => {
    return props.pointsToShow.find(
        (point) =>
            point.properties.id.toString() === props.activePointId.toString()
    );
});

const filteredPoints = computed(() => {
    return props.pointsToShow.filter((point) => {
        return (point.properties.id.toString().includes(textFilter.value) || ('name' in point.properties && point.properties.name.toString().includes(textFilter.value)))
    });
});

const resetFilters = () => {
    for(const el in localFilters.value){
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
        if(el === 'quantity'){
            localFilters.value[el].forEach(filter => {
                filter.value = true;
            })
        }
        if(el === 'area'){
            localFilters.value[el].forEach(filter => {
                filter.value = true;
            })
        }
        if(el === 'analysesObj'){
            localFilters.value[el].forEach(filter => {
                filter.value = true;
            })
        }
    };
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
    width: 30vw;
    height: 100vh;
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
    color: black;
}

.year-range {
    display: flex;

    .year-input {
        width: 8rem;
    }
}

h6 {
    text-transform: capitalize;
    margin: 0;
}
</style>
