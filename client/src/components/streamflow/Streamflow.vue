<template>
    <div
        v-if="mapLoading"
        class="loader-container"
    >
        <q-spinner
            class="map-loader"
            size="xl"
        />
    </div>
    <div>
        <div class="page-container">
            <MapFilters
                title="Water Allocations"
                :loading="pointsLoading"
                :points-to-show="features"
                :active-point-id="activePoint?.id.toString()"
                :total-point-count="pointCount"
                :filters="streamflowFilters"
                :has-area="true"
                :has-year-range="hasYearRange"
                :has-analyses-obj="true"
                @update-filter="(newFilters) => updateFilters(newFilters)"
                @select-point="(point) => selectPoint(point)"
                @view-more="getReportData()"
                @download-data="downloadSelectedPointData"
            />
            <div class="map-container">
                <MapSearch
                    v-if="allFeatures.length > 0 && streamSearchableProperties.length > 0"
                    :map="map"
                    :map-points-data="allFeatures"
                    :searchable-properties="streamSearchableProperties"
                    @select-point="(point) => activePoint = point.properties"
                />
                <Map
                    @loaded="(map) => loadPoints(map)"
                />
                <MapPointSelector
                    :points="featuresUnderCursor"
                    :open="showMultiPointPopup"
                    @close="selectPoint"
                />
            </div>
        </div>
        <StreamflowReport
            v-if="reportData"
            :active-point="activePoint"
            :report-open="reportOpen"
            :report-data="reportData"
            @close="() => {
                reportOpen = false;
                reportData = {};
            }"
        />
    </div>
</template>

<script setup>
import Map from "@/components/Map.vue";
import MapSearch from '@/components/MapSearch.vue';
import MapPointSelector from "@/components/MapPointSelector.vue";
import MapFilters from "@/components/MapFilters.vue";
import { highlightLayer, pointLayer } from "@/constants/mapLayers.js";
import { computed, ref } from "vue";
import { buildFilteringExpressions } from '@/utils/mapHelpers.js';
import { getStreamflowStations, getStreamflowReportDataById, downloadStreamflowCSV } from '@/utils/api.js';
import StreamflowReport from "./StreamflowReport.vue";

const map = ref();
const activePoint = ref();
const showMultiPointPopup = ref(false);
const featuresUnderCursor = ref([]);
const points = ref();
const allFeatures = ref([]);
const features = ref([]);
const mapLoading = ref(false);
const hasYearRange = ref(true);
const pointsLoading = ref(false);
const reportOpen = ref(false);
const reportData = ref({});
const streamSearchableProperties = [
    { label: 'Station Name', type: 'stationName', property: 'name' },
    { label: 'Station ID', type: 'stationId', property: 'id' }
];
const streamflowFilters = ref({
    buttons: [
        {
            value: true,
            label: "Historical",
            color: "blue-4",
            key: 'status',
            matches: [
                "Historical"
            ]
        },
        {
            value: true,
            label: "Active",
            color: "orange-6",
            key: 'status',
            matches: [
                "Active, Real-time, Not responding",
                "Active, Real-time, Responding",
                "Active, Non real-time"
            ]
        },
    ],
    other: {
        network: [
            {
                value: true,
                label: "Water Survey of Canada",
                key: 'net',
                matches: "Water Survey of Canada"
            },
            {
                value: true,
                label: "BC ENV - Real-time Water Data Reporting",
                key: 'net',
                matches: "BC ENV - Real-time Water Data Reporting"
            },
            {
                value: true,
                label: "Surrey SCADA",
                key: 'net',
                matches: "Surrey SCADA"
            },
            {
                value: true,
                label: "Department of Fisheries and Oceans",
                key: 'net',
                matches: "Department of Fisheries and Oceans"
            },
            {
                value: true,
                label: "BC Hydro",
                key: 'net',
                matches: "BC Hydro"
            },
            {
                value: true,
                label: "Oil and Gas Industry Network",
                key: 'net',
                matches: "Oil and Gas Industry Network"
            },
            {
                value: true,
                label: "Capital (Regional District)",
                key: 'net',
                matches: "Capital (Regional District)"
            },
            {
                value: true,
                label: "Geoscience BC",
                key: 'net',
                matches: "Geoscience BC"
            },
            {
                value: true,
                label: "Delta",
                key: 'net',
                matches: "Delta"
            },
            {
                value: true,
                label: "Wasa Lake Land Improvement District",
                key: 'net',
                matches: "Wasa Lake Land Improvement District"
            },
        ],
    },
});

const pointCount = computed(() => {
    if(points.value) return points.value.length;
    return 0;
});

/**
 * Add Watershed License points to the supplied map
 * @param mapObj Mapbox Map
 */
const loadPoints = async (mapObj) => {
    mapLoading.value = true;
    pointsLoading.value = true;
    map.value = mapObj;
    points.value = await getStreamflowStations();

    if (!map.value.getSource("point-source")) {
        const featureJson = {
            type: "geojson",
            data: points.value,
        };
        allFeatures.value = points.value.features;
        map.value.addSource("point-source", featureJson);
    }
    if (!map.value.getLayer("point-layer")) {
        map.value.addLayer(pointLayer);
        map.value.setPaintProperty("point-layer", "circle-color", [
            "match",
            ["get", "status"],
            "Active, Non real-time",
            "#FF9800",
            "Active, Real-time, Responding",
            "#FF9800",
            "Active, Real-time, Not responding",
            "#FF9800",
            "Historical",
            "#64B5F6",
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
        if(point.length === 1){
            map.value.setFilter("highlight-layer", [
                "==",
                "id",
                point[0].properties.id,
            ]);
            point[0].properties.id = point[0].properties.id.toString();
            activePoint.value = point[0].properties;
        }
        if (point.length > 1) {
            // here, point is a list of points
            featuresUnderCursor.value = point;
            showMultiPointPopup.value = true;
        }
    });

    map.value.on("mouseenter", "point-layer", () => {
        map.value.getCanvas().style.cursor = "pointer";
    });

    map.value.on("mouseleave", "point-layer", () => {
        map.value.getCanvas().style.cursor = "";
    });

    map.value.on("movestart", () => {
        pointsLoading.value = true;
    });

    map.value.on("moveend", () => {
        features.value = getVisibleLicenses();
        pointsLoading.value = false;
    });

    map.value.once('idle',  () => {
        features.value = getVisibleLicenses();
        pointsLoading.value = false;
    });
    mapLoading.value = false;
};

const getReportData = async () => {
    mapLoading.value = true;
    reportData.value = await getStreamflowReportDataById(activePoint.value.id);
    reportOpen.value = true;
    mapLoading.value = false;
}

const downloadSelectedPointData = async () => {
    await downloadStreamflowCSV(activePoint.value.id)
};

/**
 * Receive a point from the map filters component and highlight it on screen
 * @param newPoint Selected Point
 */
 const selectPoint = (newPoint) => {
    if(newPoint){
        map.value.setFilter("highlight-layer", ["==", "id", newPoint.id]);
        activePoint.value = newPoint;
        // force id as string to satisfy shared map filter component
        activePoint.value.id = activePoint.value.id.toString();
    }
    showMultiPointPopup.value = false;
};

/**
 * Gets the licenses currently in the viewport of the map
 */
const getVisibleLicenses = () => {
    const queriedFeatures = map.value.queryRenderedFeatures({
        layers: ["point-layer"],
    });

    // mapbox documentation describes potential geometry duplication when making a
    // queryRenderedFeatures call, as geometries may lay on map tile borders.
    // this ensures we are returning only unique IDs
    const uniqueIds = new Set();
    const uniqueFeatures = [];
    for (const feature of queriedFeatures) {
        const id = feature.properties['id'];
        if (!uniqueIds.has(id)) {
            uniqueIds.add(id);
            uniqueFeatures.push(feature);
        }
    }
    return uniqueFeatures;
}

/**
 * Receive changes to filters from MapFilters component and apply filters to the map
 * @param newFilters Filters passed from MapFilters
 */
 const updateFilters = (newFilters) => {
    // Not sure if updating these here matters, the emitted filter is what gets used by the map
    streamflowFilters.value = newFilters;
    const mapFilter = buildFilteringExpressions(newFilters);
    map.value.setFilter("point-layer", mapFilter);
    pointsLoading.value = true;
    setTimeout(() => {
        features.value = getVisibleLicenses();
        const selectedFeature = features.value.find(
            (feature) => feature.properties.id === activePoint.value?.id
        );
        if (selectedFeature === undefined) dismissPopup();
        pointsLoading.value = false;
    }, 500);
};

/**
 * Dismiss the map popup and clear the highlight layer
 */
const dismissPopup = () => {
    activePoint.value = null;
    map.value.setFilter("highlight-layer", false);
};
</script>

<!-- Cannot leave style tag out without breaking map for some reason -->
<style lang="scss" scoped>
.map-container {
    position: relative;

    .map {
        height: auto;
    }
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
