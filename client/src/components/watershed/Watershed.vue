<template>
    <div class="page-container">
        <Map @loaded="(map) => loadPoints(map)" />
        <div v-if="activePoint" class="point-info">
            <div class="spaced-flex-row">
                <h3>{{ activePoint.id }}</h3>
                <q-icon
                    name="close"
                    size="md"
                    class="cursor-pointer"
                    @click="activePoint = null"
                />
            </div>
            <pre>{{ activePoint }}</pre>
        </div>
    </div>
</template>

<script setup>
import Map from "@/components/Map.vue";
import { highlightLayer, pointLayer } from "@/constants/mapLayers.js";
import points from "@/constants/watershed.json";
import { ref } from "vue";

const map = ref();
const activePoint = ref();

const loadPoints = (map) => {
    if (!map.getSource("point-source")) {
        const featureJson = {
            type: "geojson",
            data: points,
        };
        map.addSource("point-source", featureJson);
    }
    if (!map.getLayer("point-layer")) {
        map.addLayer(pointLayer);
        map.setPaintProperty("point-layer", "circle-color", [
            "match",
            ["get", "term"],
            0,
            "#61913d",
            1,
            "#234075",
            "#ccc",
        ]);
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
            activePoint.value = point[0].properties;
        }
    });

    map.value = map;
};
</script>

<style lang="scss" scoped>
.point-info {
    background-color: black;
    bottom: 0;
    left: calc(50vw - 150px);
    padding: 2em;
    position: absolute;
    width: 300px;

    @media (prefers-color-scheme: light) {
        background-color: white;
        color: black;
    }
}
</style>
