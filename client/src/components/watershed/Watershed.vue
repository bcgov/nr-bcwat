<template>
    <div class="page-container">
        <Map @loaded="(map) => loadPoints(map)" />
    </div>
</template>

<script setup>
import Map from "@/components/Map.vue";
import { watershedLayer } from "@/constants/mapLayers.js";
import points from "@/constants/watershed.json";
import { ref } from "vue";

const map = ref();

const loadPoints = (map) => {
    console.log(points.features);
    map.value = map;
    if (!map.value.getSource("watershed-source")) {
        const featureJson = {
            type: "geojson",
            data: points,
        };
        map.value.addSource("watershed-source", featureJson);
    }
    if (!map.value.getLayer("watershed-layer")) {
        map.value.addLayer(watershedLayer);
    }
};
</script>

<!-- Cannot leave style tag out without breaking map for some reason -->
<style lang="scss" scoped>
.map {
    height: auto;
}
</style>
