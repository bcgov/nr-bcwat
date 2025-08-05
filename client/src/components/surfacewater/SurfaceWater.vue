<template>
    <div>
        <div class="page-container">
            <MapFilters
                title="Surface Water Stations"
                :loading="pointsLoading"
                :points-to-show="features"
                :active-point-id="activePoint?.id"
                :total-point-count="pointCount"
                :filters="surfaceWaterFilters"
                :has-analyses-obj="false"
                :view-extent-on="map?.getZoom() < 9"
                @update-filter="(newFilters) => updateFilters(newFilters)"
                @select-point="(point) => selectPoint(point)"
                @view-more="getReportData()"
                @download-data="downloadSelectedPointData"
            />
            <div class="map-container">
                <MapSearch
                    v-if="allFeatures.length > 0 && surfaceWaterSearchableProperties.length > 0"
                    :map="map"
                    :map-points-data="allFeatures"
                    :searchable-properties="surfaceWaterSearchableProperties"
                    @select-point="(point) => activePoint = point.properties"
                />
                <Map
                    :loading="mapLoading"
                    @loaded="(map) => loadPoints(map)"
                />
                <MapPointSelector
                    :points="featuresUnderCursor"
                    :open="showMultiPointPopup"
                    @close="selectPoint"
                />
            </div>
        </div>
        <WaterQualityReport
            v-if="reportData"
            :active-point="activePoint"
            :report-type="'Surface'"
            :chemistry="reportData"
            :report-open="reportOpen"
            @close="reportOpen = false"
        />
    </div>
</template>

<script setup>
import Map from "@/components/Map.vue";
import MapSearch from '@/components/MapSearch.vue';
import MapPointSelector from '@/components/MapPointSelector.vue';
import MapFilters from '@/components/MapFilters.vue';
import { highlightLayer, pointLayer } from "@/constants/mapLayers.js";
import WaterQualityReport from "@/components/waterquality/WaterQualityReport.vue";
import { buildFilteringExpressions } from '@/utils/mapHelpers.js';
import { getSurfaceWaterStations, getSurfaceWaterReportDataById, getSurfaceWaterStationStatistics, downloadSurfaceWaterCSV } from '@/utils/api.js';
import { computed, ref } from 'vue';

const map = ref();
const mapLoading = ref(false);
const activePoint = ref();
const showMultiPointPopup = ref(false);
const features = ref([]);
const allFeatures = ref([]);
const allQueriedPoints = ref();
const featuresUnderCursor = ref([]);
const surfaceWaterPoints = ref();
const pointsLoading = ref(false);
const reportOpen = ref(false);
const reportData = ref();
// page-specific data search handlers
const surfaceWaterSearchableProperties = [
    { label: 'Station Name', type: 'stationName', property: 'name' },
    { label: 'Station ID', type: 'stationId', property: 'id' }
];
const surfaceWaterFilters = ref({
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
        {
            value: true,
            label: "Not Available",
            color: "grey-6",
            key: 'status',
            matches: [
                "Not Available"
            ]
        },
    ],
    other: {
        network: [
            {
                value: true,
                label: "Lake Windemere Ambassadors",
                key: 'net',
                matches: "Lake Windemere Ambassadors"
            },
            {
                value: true,
                label: "BC Environmental Assessment Office (EAO)",
                key: 'net',
                matches: "BC Environmental Assessment Office (EAO)"
            },
            {
                value: true,
                label: "Friends of Swan Creek",
                key: 'net',
                matches: "Friends of Swan Creek"
            },
            {
                value: true,
                label: "Northern Health Authority",
                key: 'net',
                matches: "Northern Health Authority"
            },
            {
                value: true,
                label: "Regulator – BC Oil and Gas Commission",
                key: 'net',
                matches: "Regulator – BC Oil and Gas Commission"
            },
            {
                value: true,
                label: "ECCC - National Long-term Water Quality Monitoring Data",
                key: 'net',
                matches: "ECCC - National Long-term Water Quality Monitoring Data"
            },
            {
                value: true,
                label: "Mackenzie DataStream",
                key: 'net',
                matches: "Mackenzie DataStream"
            },
            {
                value: true,
                label: "Village of Belcarra",
                key: 'net',
                matches: "Village of Belcarra"
            },
            {
                value: true,
                label: "Friends of Tod Creek Watershed",
                key: 'net',
                matches: "Friends of Tod Creek Watershed"
            },
            {
                value: true,
                label: "Columbia Lake Stewardship Society",
                key: 'net',
                matches: "Columbia Lake Stewardship Society"
            },
            {
                value: true,
                label: "Friends of Kootenay Lake",
                key: 'net',
                matches: "Friends of Kootenay Lake"
            },
        ],
    },
});

const pointCount = computed(() => {
    if(surfaceWaterPoints.value) return surfaceWaterPoints.value.length;
    return 0;
});

/**
 * Add Watershed License points to the supplied map
 * @param mapObj Mapbox Map
 */
 const loadPoints = async (mapObj) => {
    mapLoading.value = true;
    map.value = mapObj;
    surfaceWaterPoints.value = await getSurfaceWaterStations();

    if (!map.value.getSource("point-source")) {
        const featureJson = {
            type: "geojson",
            data: surfaceWaterPoints.value,
        };
        allFeatures.value = surfaceWaterPoints.value.features;
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

    map.value.on("click", "point-layer", async (ev) => {
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
        if (map.value.getZoom() > 9) pointsLoading.value = true;
    });

    map.value.on("moveend", () => {
        features.value = getVisibleLicenses();
    });

    map.value.once('idle',  () => {
        features.value = getVisibleLicenses();
    });
    mapLoading.value = false;
};

const getReportData = async () => {
    mapLoading.value = true;
    reportData.value = await getSurfaceWaterReportDataById(activePoint.value.id);
    reportOpen.value = true;
    mapLoading.value = false;
}

/**
 * Receive a point from the map filters component and highlight it on screen
 * @param newPoint Selected Point
 */
 const selectPoint = async (newPoint) => {
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
    if (allQueriedPoints.value && map.value.getZoom() < 9) {
        pointsLoading.value = false;
        return allQueriedPoints.value;
    }

    pointsLoading.value = true;
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
    // Set allQueriedPoints on the initial map load
    if (!allQueriedPoints.value) allQueriedPoints.value = uniqueFeatures;
    pointsLoading.value = false;
    return uniqueFeatures;
};

/**
 * Receive changes to filters from MapFilters component and apply filters to the map
 * @param newFilters Filters passed from MapFilters
 */
 const updateFilters = (newFilters) => {
    // Not sure if updating these here matters, the emitted filter is what gets used by the map
    surfaceWaterFilters.value = newFilters;
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


const downloadSelectedPointData = async () => {
    await downloadSurfaceWaterCSV(activePoint.value.id)
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
.map {
    height: auto;
}
</style>
