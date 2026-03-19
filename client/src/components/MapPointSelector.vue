<template>
    <q-dialog
        :model-value="props.open"
        @update:model-value="emit('close')"
    >
        <q-card
            class="popup-content"
            square
        >
            <q-card-section
                class="header"
            >
                <div class="spaced-flex-row">
                    <div class="text-h6">{{ props.points.length }} points at these coordinates</div>
                    <q-btn
                        icon="close"
                        flat
                        @click="emit('close')"
                    />
                </div>
            </q-card-section>
            <q-card-section
                class="points-list"
            >
                <q-list
                    separator
                >
                    <q-item
                        v-for="point in props.points"
                        :key="point.id"
                        clickable
                        @click="() => selectPoint(point)"
                    >
                        <q-item-section>
                            <div v-if="props.page === 'watershed'">
                                <q-item-label v-if="'lic' in point.properties">{{ point.properties.lic }}</q-item-label>
                                <q-item-label
                                    class="item-label"
                                    caption
                                >
                                    <div v-if="'org' in point.properties">
                                        {{ point.properties.org }}
                                    </div>
                                    <div
                                        v-if="'qty' in point.properties && point.properties.qty > 0"
                                        data-cy="point-qty"
                                    >
                                        Quantity: {{ point.properties.qty }} m³/year
                                    </div>
                                    <div v-if="'src_name' in point.properties">
                                        Source: {{ point.properties.src_name }}
                                    </div>
                                    <div v-if="'nid' in point.properties">
                                        Licence: <span>({{ point.properties.nid }})</span>
                                    </div>
                                    <div v-if="'pod' in point.properties">
                                        POD: {{ point.properties.pod }}
                                    </div>
                                </q-item-label>
                            </div>
                            <div v-else-if="props.page === 'waterportal'">
                                <q-item-label v-if="'name' in point.properties"> {{ point.properties.name }} </q-item-label>
                                <q-item-label
                                    class="item-label"
                                    caption
                                >
                                    <div
                                        v-if="'yr' in point.properties"
                                        data-cy="point-yr"
                                    >
                                        Year Range: {{ yearRangeString(JSON.parse(point.properties.yr)) }}
                                    </div>
                                    <div
                                        v-if="'area' in point.properties"
                                        data-cy="point-area"
                                    >
                                        Area: {{ point.properties.area.toFixed(1) }}km<sup>2</sup>
                                    </div>
                                    <div v-if="'net' in point.properties">
                                        Network: {{ point.properties.net }}
                                    </div>
                                </q-item-label>
                            </div>
                        </q-item-section>
                    </q-item>
                </q-list>
            </q-card-section>
        </q-card>
    </q-dialog>
</template>

<script setup>
import { yearRangeString } from "@/utils/stringHelpers.js";

const emit = defineEmits(['close']);

const props = defineProps({
    points: {
        type: Array,
        default: () => [{
            name: 'Point Name go here',
            data: {
                properties: {},
                geometry: {},
            },
        }],
    },
    open: {
        type: Boolean,
        default: false,
    },
    page: {
        type: String,
        default: '',
    },
});

const selectPoint = (point) => {
    console.log(point)
    emit('close', point);
}

</script>

<style lang="scss" scoped>
.header {
    background-color: $primary;
    color: white;
}
.popup-content {
    overflow: hidden;
}
.points-list {
    max-height: 22rem;
    overflow-y: auto;
}
</style>
