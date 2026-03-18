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
                <div class="row">
                    <div class="text-h6">{{ props.points.length }} points at these coordinates</div>
                    <q-space />
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
                            <q-item-label v-if="'name' in point.properties"> Name: {{ point.properties.name }} </q-item-label>
                            <q-item-label> ID: {{ point.properties.id }} </q-item-label>
                            <q-item-label caption> 
                                <q-icon name="location_on"/> {{ point.geometry.coordinates[0].toFixed(4) }}, {{ point.geometry.coordinates[1].toFixed(4) }}
                            </q-item-label>
                            <div v-if="props.page === 'watershed'">
                                <q-item-label
                                    class="item-label"
                                >
                                    <div>
                                        <span v-if="'org' in point.properties">
                                            {{ point.properties.org }}
                                        </span>
                                        <span class="q-mx-sm">∙</span>
                                        <span v-if="'qty' in point.properties && point.properties.qty > 0">
                                            {{ point.properties.qty }} m³/year
                                        </span>
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
                                <q-item-label v-if="'yr' in point.properties">
                                    Year Range: {{ JSON.parse(point.properties.yr)[0] }}-{{ JSON.parse(point.properties.yr)[JSON.parse(point.properties.yr).length - 1] }}
                                </q-item-label>
                                <q-item-label v-if="'area' in point.properties">
                                    Area: {{ point.properties.area.toFixed(1) }}km<sup>2</sup>
                                </q-item-label>
                                <q-item-label v-if="'net' in point.properties">
                                    Network: {{ point.properties.net }}
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
    max-height: 20rem;
    overflow-y: auto;
}
</style>
