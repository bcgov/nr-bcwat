<template>
    <div class="map-filters-container">
        <div class="row justify-between">
            <h3>Water Allocations</h3>
            <q-btn icon="mdi-filter">
                <q-menu>
                    <div
                        v-if="Object.keys(localFilters).length > 0"
                        class="filter-menu"
                    >
                        <q-checkbox
                            v-model="localFilters.surfaceWater"
                            label="Surface Water"
                        /></div
                ></q-menu>
            </q-btn>
        </div>
        <div>{{ props.filters }}</div>
        <div>
            {{ props.pointsToShow.length }}
        </div>
        <div v-for="point in pointsToShow" :key="point.properties.id">
            <pre>{{ point.properties.nid }}</pre>
            <pre>{{ point.properties }}</pre>
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
    pointsToShow: {
        type: Object,
        default: () => {},
    },
});

const emit = defineEmits(["update-filter"]);

const localFilters = ref({});

onMounted(() => {
    localFilters.value = props.filters;
});
</script>

<style lang="scss" scoped>
.map-filters-container {
    background-color: black;
    padding: 1em;
    width: 30vw;
    height: 100vh;
    overflow-y: auto;

    @media (prefers-color-scheme: light) {
        background-color: white;
        color: black;
    }
}
</style>
