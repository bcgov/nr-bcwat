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
            <div
                v-if="activePoint"
                class="selected-point"
            >
                <pre>{{ activePoint.properties.nid }}</pre>
                <pre>{{ activePoint.properties }}</pre>
                <q-btn 
                    label="View More"
                    color="primary"
                    @click="emit('view-more')"
                />
            </div>
            <div class="row justify-between">
                <h3>Water Allocations</h3>
                <q-btn
                    icon="mdi-filter"
                    flat
                >
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
                                    @update:model-value="emit('update-filter', localFilters)"
                                />
                            </div></div
                    ></q-menu>
                </q-btn>
            </div>
            <div>
                <i>{{ props.pointsToShow.length }} Stations in Map Range</i>
            </div>

            <q-input
                v-model="textFilter"
                label="Search"            
                label-color="primary"
                dense
            />
        </div>
        
        <!-- The max-height property of this to determine how much content to render in the virtual scroll -->
        <q-virtual-scroll
            :items="filteredPoints"
            v-slot="{ item, index }"
            style="max-height: 90%;"
            separator
            :virtual-scroll-item-size="50"
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

        <q-inner-loading
            :showing="props.loading"
        />
    </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";

const props = defineProps({
    loading: {
        type: Boolean,
        default: false,
    },
    title: {
        type: String,
        default: '',
    },
    filters: {
        type: Object,
        default: () => {},
    },
    activePointId: {
        type: String,
        default: '',
    },
    pointsToShow: {
        type: Object,
        default: () => {},
    },
    totalPointCount: {
        type: Number,
        default: 0,
    },
});

const emit = defineEmits(["update-filter", "select-point", "view-more"]);

const localFilters = ref({});
const textFilter = ref('');

onMounted(() => {
    localFilters.value = props.filters;
});

const activePoint = computed(() => {
    return props.pointsToShow.find(point => point.properties.id === props.activePointId)
});

const filteredPoints = computed(() => {
    if (!textFilter.value) return props.pointsToShow.filter(point => point.properties.id !== props.activePointId);
    return props.pointsToShow.filter(point => point.properties.id !== props.activePointId && point.properties.id.includes(textFilter.value))
});
</script>

<style lang="scss" scoped>
.map-filters-container {
    background-color: black;
    display: flex;
    flex-direction: column;
    // padding: 1em;
    width: 30vw;
    height: 100vh;

    @media (prefers-color-scheme: light) {
        background-color: white;
        color: black;
    }
}

// Causes the div to be the scrollable part of its parent div
.flex-scroll {
    flex: 1 1 auto;
    overflow-y: auto;
}

.filter-menu {
    color: black;
    padding: 1em;

    @media (prefers-color-scheme: light) {
        background-color: white;
        color: black;
    }
}

.selected-point {
    border: 1px solid white;
    border-radius: 0.3em;
    padding: 0.5em;

    @media (prefers-color-scheme: light) {
        border: 1px solid  black;
    }
}

.station-container {
    cursor: pointer;

    &:hover {
        background-color: grey;
    }
}

.item-label {
    color: white;

    @media (prefers-color-scheme: light) {
        color: black;
    }
}

h6 {
    text-transform: capitalize;
    margin: 0;
}
</style>
