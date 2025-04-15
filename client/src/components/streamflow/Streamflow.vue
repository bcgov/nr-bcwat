<template>
    <div class="page-container">
        <Map @loaded="(map) => loadPoints(map)" />
        <div v-if="activePoint" class="point-info">
            <div class="spaced-flex-row">
                <h3>{{ activePoint.name }}</h3>
                <q-icon
                    name="close"
                    size="md"
                    class="cursor-pointer"
                    @click="activePoint = null"
                />
            </div>
            <div class="point-details">
                <div>
                    <span class="text-bold">ID</span>: {{ activePoint.id }}
                </div>
                <div>
                    <span class="text-bold">NID</span>: {{ activePoint.nid }}
                </div>
                <div>
                    <span class="text-bold">Area</span>:
                    {{ activePoint.area }}km<sup>2</sup>
                </div>
            </div>
            <q-btn
                class="q-mt-lg"
                label="View More"
                color="secondary"
                @click="openReportModal"
            />
        </div>

        <div
            v-if="showStreamflowDetails"
            class="streamflow-details"
            transition-show="jump-down"
            transition-hide="jump-up"
        >
            <div class="row">
                Content to go here.
                <q-space />
                <q-btn
                    class="q-ma-sm"
                    icon="close"
                    color="primary"
                    @click="() => (showStreamflowDetails = false)"
                />
            </div>
        </div>
    </div>
</template>

<script setup>
import Map from "@/components/Map.vue";
import { highlightLayer, pointLayer } from "@/constants/mapLayers.js";
import points from "@/constants/streamflow.json";
import { ref } from "vue";

const map = ref();
const activePoint = ref();
const showStreamflowDetails = ref(false);

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

const openReportModal = () => {
    showStreamflowDetails.value = true;
};
</script>

<!-- Cannot leave style tag out without breaking map for some reason -->
<style lang="scss" scoped>
.map {
    height: auto;
}

.streamflow-details {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 10 !important;
    background-color: grey;
}
</style>
