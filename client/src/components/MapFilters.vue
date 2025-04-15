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
                            @update:model-value="
                                emit('update-filter', localFilters)
                            "
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
                                @update:model-value="
                                    emit('update-filter', localFilters)
                                "
                            />
                        </div></div
                ></q-menu>
            </q-btn>
        </div>
        <div>
            <i>Showing {{ props.pointsToShow.length }} / {{ props.totalPointCount }} Points</i>
        </div>
        <div v-for="point in pointsToShow" :key="point.properties.id">
            <hr />
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
    totalPointCount: {
        type: Number,
        default: 0,
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
</style>
