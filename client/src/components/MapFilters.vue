<template>
    <div class="map-filters-container">
        <div class="spaced-flex-row">
            <h3>Water Allocations</h3>
            <q-btn icon="mdi-filter">
                <q-menu> <div class="filter-menu">Menu</div></q-menu>
            </q-btn>
        </div>
        {{ props.pointsToShow.length }}
        <div v-for="point in pointsToShow">
            <pre>{{ point.properties.nid }}</pre>
            <pre>{{ point.properties }}</pre>
        </div>
    </div>
</template>

<script setup>
const props = defineProps({
    pointsToShow: {
        type: Object,
        default: () => {},
    },
});
</script>

<style lang="scss" scoped>
.map-filters-container {
    background-color: black;
    padding: 1em;
    width: 20rem;
    height: 100vh;
    overflow-y: auto;

    @media (prefers-color-scheme: light) {
        background-color: white;
        color: black;
    }
}
</style>
