<template>
    <div class="map-filters-container">
        <div class="row justify-between">
            <h3>Water Allocations</h3>
            <q-btn icon="mdi-filter">
                <q-menu>
                    <div v-if="localFilters.buttons" class="filter-menu">
                        <h6>Water Allocations</h6>
                        <q-checkbox
                            v-for="button in localFilters.buttons"
                            :key="button"
                            v-model="button.value"
                            :label="button.label"
                            :color="button.color"
                            @update:model-value="emit('update-filter', localFilters)"
                        />
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
        <div
            v-for="point in pointsToShow.filter(point => point.properties.id === props.activePointId)"
            :key="point.properties.id"
            class="selected-point"
        >
            <h6>Selected Point</h6>
            <hr />
            <pre>{{ point.properties.nid }}</pre>
            <pre>{{ point.properties }}</pre>
        </div>
        <div class="flex-scroll">
            <div
                v-for="point in pointsToShow.filter(point => point.properties.id !== props.activePointId)"
                :key="point.properties.id"
                @click="emit('select-point', point)"
            >
                <hr />
                <pre>{{ point.properties.nid }}</pre>
                <pre>{{ point.properties }}</pre>
            </div>
        </div>
    </div>
</template>

<script setup>
import { onMounted, ref } from "vue";

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

const emit = defineEmits(["update-filter", "select-point"]);

const localFilters = ref({});

onMounted(() => {
    localFilters.value = props.filters;
});
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

    h6 {
        text-transform: capitalize;
        margin: 0;
    }

    @media (prefers-color-scheme: light) {
        background-color: white;
        color: black;
    }
}

.selected-point {
    background-color: aqua;
}
</style>
