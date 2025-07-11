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
            <div v-if="activePoint" class="selected-point">
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
                    Status: {{ activePoint.properties.status }}
                </div>
                <div v-if="'qty' in activePoint.properties">
                    Quantity: {{ activePoint.properties.qty }}
                </div>
                <div v-if="'st' in activePoint.properties">
                    Status: {{ activePoint.properties.st }}
                </div>
                <div v-if="'term' in activePoint.properties">
                    Term: {{ activePoint.properties.term }}
                </div>
                <div v-if="'yr' in activePoint.properties">
                    Year Range: {{ JSON.parse(activePoint.properties.yr)[0] }} - {{ JSON.parse(activePoint.properties.yr)[1] }}
                </div>
                <q-btn
                    v-if="props.viewMore"
                    label="View More"
                    color="primary"
                    @click="emit('view-more')"
                />
            </div>
            <div class="row justify-between">
                <h3>Filtered {{ props.title }}</h3>
                <q-btn icon="mdi-filter" flat>
                    <q-menu>
                        <div v-if="localFilters.other" class="filter-menu">
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
import { computed, onMounted, ref, watch } from "vue";

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
    hasYearRange: {
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

onMounted(() => {
    localFilters.value = props.filters;
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
    padding: 1em;
}

.selected-point {
    border: 1px solid black;
    border-radius: 0.3em;
    padding: 0.5em;
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
