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
        <!-- The max-height property of this to determine how much content to render in the virtual scroll -->
        <q-virtual-scroll
            :items="pointsToShow"
            v-slot="{ item, index }"
            style="max-height: 90%;"
            separator
            :virtual-scroll-item-size="50"
        >
            <q-item
                :key="index"
                clickable
                @mouseover="() => console.log(item.properties.id)"
            >
                <q-item-section>
                    <q-item-label>
                        Allocation ID: {{ item.properties.nid }}
                    </q-item-label>
                    <q-item-label :style="`color: white;`" caption>
                        ID: {{ item.properties.id }}
                    </q-item-label>
                    <q-item-label :style="`color: white;`" caption>
                        Net: {{ item.properties.net }}
                    </q-item-label>
                    <q-item-label :style="`color: white;`" caption>
                        Type: {{ item.properties.type }}
                    </q-item-label>
                </q-item-section>
            </q-item>
        </q-virtual-scroll>
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
