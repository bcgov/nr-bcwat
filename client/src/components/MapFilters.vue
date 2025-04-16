<template>
    <div class="map-filters-container">
        <div v-if="localFilters.buttons">
            <h6>Water Allocations</h6>
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
            <q-btn icon="mdi-filter">
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
            <i>Showing {{ props.pointsToShow.length }} / {{ props.totalPointCount }} Points</i>
        </div>

        <q-input
            v-model="textFilter"
            label="Search"
            text-color="white-1"
            color="white-1"
            label-color="white-1"
            bg-color="white-1"
            dark
            dense
        />
        
        <div class="flex-scroll">
            <div
                v-for="point in pointsToShow.filter(point => point.properties.id !== props.activePointId)"
                :key="point.properties.id"
                class="station-container"
                @click="emit('select-point', point)"
            >
                <hr />
                <pre>{{ point.properties.nid }}</pre>
                <pre>ID: {{ point.properties.id }}</pre>
            </div>
        </div>
    </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";

const props = defineProps({
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

})
</script>

<style lang="scss" scoped>
.map-filters-container {
    background-color: black;
    display: flex;
    flex-direction: column;
    padding: 1em;
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
    padding: 0.5em;
}

.station-container {
    cursor: pointer;
}

h6 {
    text-transform: capitalize;
    margin: 0;
}
</style>
