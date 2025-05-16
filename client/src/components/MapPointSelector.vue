<template>
    <q-dialog
        :model-value="props.open"
        @update:model-value="emit('close')"
    >
        <q-card class="popup-content">
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
                <q-list>
                    <q-item
                        v-for="point in props.points"
                        clickable
                        @click="() => selectPoint(point.properties)"
                    >
                        <q-item-section>
                            <q-item-label v-if="'name' in point.properties"> Name: {{ point.properties.name }} </q-item-label>
                            <q-item-label> ID: {{ point.properties.id }} </q-item-label>
                            <q-item-label caption> 
                                <q-icon name="location_on"/> {{ point.geometry.coordinates[0], point.geometry.coordinates[1] }}
                            </q-item-label>
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
    }
});

const selectPoint = (point) => {
    emit('close', point);
}

</script>

<style lang="scss">
.popup-content {
    overflow: hidden;
}
.points-list {
    max-height: 20rem;
    overflow-y: auto;
}
</style>
