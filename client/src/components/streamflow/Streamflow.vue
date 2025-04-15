<template>
    <div>
        <div class="page-container">
            <Map @loaded="(map) => loadPoints(map)" />
            <div v-if="activePoint" class="point-info">
                <div class="spaced-flex-row">
                    <h3>{{ activePoint.name }}</h3>
                    <q-icon
                        name="close"
                        size="md"
                        class="cursor-pointer"
                        @click="dismissPopup()"
                    />
                </div>
                <div class="point-details">
                    <div>
                        <span class="text-bold">ID</span>: {{ activePoint }}
                    </div>
                    <div>
                        <span class="text-bold">NID</span>: {{ activePoint }}
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
            <MapFilters
                :points-to-show="features"
                :filters="streamflowFilters"
                @update-filter="(newFilters) => updateFilters(newFilters)"
            />
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
                        <!-- <p>{{ activePoint.area }} km<sup>2</sup></p> -->
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
                    <span class="about"
                        ><q-icon name="help" /> About this page
                        <q-tooltip>About this page content goes here.</q-tooltip>
                    </span>
                </div>
                <div class="data-license cursor-pointer">Data License</div>
            </div>
            <q-tab-panels v-model="viewPage">
                <q-tab-panel name="sevenDayFlow">
                    <SevenDayFlow />
                </q-tab-panel>
                <q-tab-panel name="flowDurationTool">
                    <FlowDurationTool />
                </q-tab-panel>
                <q-tab-panel name="flowMetrics">
                    <FlowMetrics />
                </q-tab-panel>
                <q-tab-panel name="monthlyMeanFlow">
                    <MonthlyMeanFlow />
                </q-tab-panel>
                <q-tab-panel name="stage">
                    <StreamflowStage />
                </q-tab-panel>
            </q-tab-panels>
        </div>
    </div>
</template>

<script setup>
import Map from "@/components/Map.vue";
import MapFilters from "@/components/MapFilters.vue";
import { highlightLayer, pointLayer } from "@/constants/mapLayers.js";
import points from "@/constants/streamflow.json";
import { ref } from "vue";
import SevenDayFlow from "./SevenDayFlow.vue";
import FlowDurationTool from "./FlowDurationTool.vue";
import FlowMetrics from "./FlowMetrics.vue";
import MonthlyMeanFlow from "./MonthlyMeanFlow.vue";
import StreamflowStage from "./StreamflowStage.vue";

const map = ref();
const activePoint = ref();
const features = ref([]);
const showStreamflowDetails = ref(false);
const viewPage = ref('');
const streamflowFilters = ref({
    buttons: [
        {
            value: true,
            label: "Surface Water",
        },
        {
            value: true,
            label: "Ground Water",
        },
    ],
    other: {
        type: [
            {
                value: true,
                label: "License",
            },
            {
                value: true,
                label: "Short Term Application",
            },
        ],
        purpose: [
            {
                value: true,
                label: "Agriculture",
            },
            {
                value: true,
                label: "Commerical",
            },
            {
                value: true,
                label: "Domestic",
            },
            {
                value: true,
                label: "Municipal",
            },
            {
                value: true,
                label: "Power",
            },
            {
                value: true,
                label: "Oil & Gas",
            },
            {
                value: true,
                label: "Storage",
            },
            {
                value: true,
                label: "Other",
            },
        ],
        agency: [
            {
                value: true,
                label: "BC Ministry of Forests",
            },
            {
                value: true,
                label: "BC Energy Regulator",
            },
        ],
        status: [
            {
                value: true,
                label: "Application",
            },
            {
                value: true,
                label: "Current",
            },
        ],
    },
});

/**
 * Add Watershed License points to the supplied map
 * @param mapObj Mapbox Map
 */
const loadPoints = (mapObj) => {
    console.log("KSM")
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

    console.log("KSM")
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

/**
 * Receive changes to filters from MapFilters component and apply filters to the map
 * @param newFilters Filters passed from MapFilters
 */
 const updateFilters = (newFilters) => {
    // Not sure if updating these here matters, the emitted filter is what gets used by the map
    watershedFilters.value = newFilters;

    const mapFilter = ["any"];
    map.value.setFilter("point-layer", mapFilter);
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

.data-license {
    display: flex;
    height: 100%;
    align-items: end;
    text-decoration: underline;
}

.about {
    cursor: pointer;
}
</style>
