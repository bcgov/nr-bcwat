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
                    @click="dismissPopup()"
                />
            </div>
            <pre>{{ activePoint }}</pre>
            <q-btn
                label="View Report"
                color="primary"
                @click="reportOpen = true"
            />
        </div>
    </div>
    <WatershedReport :report-open="reportOpen" @close="reportOpen = false" />
</template>

<script setup>
import Map from "@/components/Map.vue";
import WatershedReport from "@/components/watershed/WatershedReport.vue";
import { highlightLayer, pointLayer } from "@/constants/mapLayers.js";
import points from "@/constants/watershed.json";
import { ref } from "vue";

const map = ref();
const activePoint = ref();
const reportOpen = ref(false);

/**
 * Add Watershed License points to the supplied map
 * @param mapObj Mapbox Map
 */
const loadPoints = (mapObj) => {
    map.value = mapObj;
    if (!map.value.getSource("point-source")) {
        const featureJson = {
            type: "geojson",
            data: points,
        };
        map.value.addSource("point-source", featureJson);
    }
    if (!map.value.getLayer("point-layer")) {
        map.value.addLayer(pointLayer);
        map.value.setPaintProperty("point-layer", "circle-color", [
            "match",
            ["get", "term"],
            0,
            "#61913d",
            1,
            "#234075",
            "#ccc",
        ]);
    }
    if (!map.value.getLayer("highlight-layer")) {
        map.value.addLayer(highlightLayer);
    }

    map.value.on("click", "point-layer", (ev) => {
        const point = map.value.queryRenderedFeatures(ev.point, {
            layers: ["point-layer"],
        });

        if (point.length > 0) {
            map.value.setFilter("highlight-layer", [
                "==",
                "id",
                point[0].properties.id,
            ]);
            activePoint.value = point[0].properties;
        }
    });
};

/**
 * Dismiss the map popup and clear the highlight layer
 */
const dismissPopup = () => {
    activePoint.value = null;
    map.value.setFilter("highlight-layer", false);
};
</script>

<style lang="scss" scoped>
.point-info {
    background-color: black;
}
</style>
