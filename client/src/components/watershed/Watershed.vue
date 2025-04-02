<template>
    <div class="page-container">
        <Map @loaded="(map) => loadPoints(map)" />
    </div>
</template>

<script setup>
import Map from "@/components/Map.vue";
import { highlightLayer, pointLayer } from "@/constants/mapLayers.js";
import points from "@/constants/watershed.json";
import { ref } from "vue";

const map = ref();

const loadPoints = (map) => {
    console.log(points.features);
    if (!map.getSource("point-source")) {
        const featureJson = {
            type: "geojson",
            data: points,
        };
        map.addSource("point-source", featureJson);
    }
    if (!map.getLayer("point-layer")) {
        map.addLayer(pointLayer);
    }
    if (!map.getLayer("highlight-layer")) {
        map.addLayer(highlightLayer);
    }

    map.on("click", "point-layer", (ev) => {
        const point = map.queryRenderedFeatures(ev.point, {
            layers: ["point-layer"],
        });

        if (point.length > 0) {
            map.setFilter("highlight-layer", [
                "==",
                "id",
                point[0].properties.id,
            ]);
        }
    });

    map.value = map;
};
</script>

<!-- Cannot leave style tag out without breaking map for some reason -->
<style lang="scss" scoped>
.map {
    height: auto;
}
</style>
