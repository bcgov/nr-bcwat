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
                @click="() => (showStreamflowDetails = true)"
            />
        </div>
    </div>
    <div
        class="report-container row"
        :class="showStreamflowDetails ? 'open' : ''"
    >
        <div v-if="activePoint" class="sidebar col-3">
            <q-btn
                class="q-mb-md"
                color="white"
                flat
                label="Back to Map"
                icon="reply"
                dense
                @click="() => (showStreamflowDetails = false)"
            />
            <div class="text-h5 text-bold">
                Watershed {{ activePoint.name }}
            </div>
            <div class="text-h5 subtitle">ID: {{ activePoint.nid }}</div>
            <div class="header-grid">
                <div v-if="'network' in activePoint" class="col">
                    <div class="text-h6">Network</div>
                    <p>{{ activePoint.network }}</p>
                </div>
                <div v-if="'yr' in activePoint" class="col">
                    <div class="text-h6">Year Range</div>
                    <p>
                        {{ activePoint.yr.substring(1, 5) }} -
                        {{ activePoint.yr.substring(6, 10) }}
                    </p>
                </div>
                <div v-if="'status' in activePoint" class="col">
                    <div class="text-h6">Status</div>
                    <p>{{ activePoint.status }}</p>
                </div>
                <div v-if="'area' in activePoint" class="col">
                    <div class="text-h6">Area</div>
                    <p>{{ activePoint.area }} km<sup>2</sup></p>
                </div>
                <div v-if="'net' in activePoint" class="col">
                    <div class="text-h6">Mean Annual Discharge</div>
                    <p>{{ activePoint.net }} m<sup>3</sup>/s</p>
                </div>
            </div>
            <q-separator color="white" />
            <q-list class="q-mt-sm">
                <q-item clickable @click="() => (viewPage = 'sevenDayFlow')">
                    <div class="text-h6">Seven Day Flow</div>
                </q-item>
                <q-item
                    clickable
                    @click="() => (viewPage = 'flowDurationTool')"
                >
                    <div class="text-h6">Flow Duration Tool</div>
                </q-item>
                <q-item clickable @click="() => (viewPage = 'flowMetrics')">
                    <div class="text-h6">Flow Metrics</div>
                </q-item>
                <q-item clickable @click="() => (viewPage = 'monthlyMeanFlow')">
                    <div class="text-h6">Monthly Mean Flow</div>
                </q-item>
                <q-item clickable @click="() => (viewPage = 'stage')">
                    <div class="text-h6">Stage</div>
                </q-item>
            </q-list>
            <div>
                <p>
                    <q-icon name="help" /> About this page
                    <q-tooltip>About this page content goes here.</q-tooltip>
                </p>
            </div>
        </div>
        <div>Chart content to go here.</div>
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
