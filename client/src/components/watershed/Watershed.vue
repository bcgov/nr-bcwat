<template>
    <div>
        <div class="page-container">
            <Map @loaded="(map) => loadPoints(map)" />
            <div v-if="activePoint" class="point-info">
                <div class="row justify-between">
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
            <MapFilters
                :points-to-show="features"
                :filters="watershedFilters"
            />
        </div>
        <WatershedReport
            :report-open="reportOpen"
            @close="reportOpen = false"
        />
    </div>
</template>

<script setup>
import Map from "@/components/Map.vue";
import MapFilters from "@/components/MapFilters.vue";
import WatershedReport from "@/components/watershed/WatershedReport.vue";
import { highlightLayer, pointLayer } from "@/constants/mapLayers.js";
import points from "@/constants/watershed.json";
import { ref } from "vue";
import mapboxgl from "mapbox-gl";

const map = ref();
const activePoint = ref();
const reportOpen = ref(false);
const features = ref([]);
const watershedFilters = ref({
    surfaceWater: true,
    groundWater: true,
    type: {
        license: true,
        shortTerm: true,
    },
    purpose: {
        agriculture: true,
        commercial: true,
        domestic: true,
        municipal: true,
        power: true,
        oilgas: true,
        storage: true,
        other: true,
    },
    agency: {
        mof: true,
        er: true,
    },
    status: {
        application: true,
        current: true,
    },
});

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
        setTimeout(() => {
            features.value = map.value.queryRenderedFeatures({
                layers: ["point-layer"],
            });
        }, 1000);
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

    map.value.on("mouseenter", "point-layer", () => {
        map.value.getCanvas().style.cursor = "pointer";
    });

    map.value.on("mouseleave", "point-layer", () => {
        map.value.getCanvas().style.cursor = "";
    });

    map.value.on("moveend", (ev) => {
        // console.log(ev);
        // console.log(map.value.getBounds());
        features.value = map.value.queryRenderedFeatures({
            layers: ["point-layer"],
        });
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
