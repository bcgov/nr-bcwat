<template>
    <div>
        <div class="page-container">
            <MapFilters
                v-if="map"
                title="Ground Water Quality"
                paragraph="Points on the map represent groundwater quality monitoring stations. Control which stations are visible using the checkboxes and filter below. Click any marker on the map, or item in the list below, to access monitoring data."
                :all-points="groundWaterPoints"
                :loading="pointsLoading"
                :points-to-show="features"
                :active-point-id="activePoint?.id"
                :total-point-count="pointCount"
                :filters="groundWaterFilters"
                :has-analyses-obj="false"
                :view-extent-on="map?.getZoom() < 9"
                @update-filter="(newFilters) => updateFilters(newFilters)"
                @select-point="(point) => selectPoint(point)"
                @view-more="getReportData()"
                @download-data="downloadSelectedPointData"
            />
            <div class="map-container">
                <MapSearch
                    v-if="map && allFeatures.length > 0 && groundWaterSearchableProperties.length > 0"
                    :map="map"
                    :map-points-data="allFeatures"
                    :searchable-properties="groundWaterSearchableProperties"
                    @select-point="(point) => activePoint = point.properties"
                    @place-marker="createMarker"
                />
                <Map
                    current-section="ground-water-quality"
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
            v-if="activePoint && reportData"
            :active-point="activePoint"
            :chemistry="reportData"
            :report-open="reportOpen"
            :report-type="'Ground'"
            @close="reportOpen = false; reportData = null"
        />
    </div>
</template>

<script setup>
import Map from "@/components/Map.vue";
import MapSearch from '@/components/MapSearch.vue';
import MapPointSelector from '@/components/MapPointSelector.vue';
import MapFilters from '@/components/MapFilters.vue';
import mapboxgl from 'mapbox-gl';
import { highlightLayer, pointLayer } from "@/constants/mapLayers.js";
import { buildFilteringExpressions } from '@/utils/mapHelpers.js';
import { getGroundWaterQualityStations, getGroundWaterQualityReportById, downloadGroundwaterQualityCSV } from '@/utils/api.js';
import WaterQualityReport from "@/components/waterquality/WaterQualityReport.vue";
import { computed, ref } from 'vue';

const map = ref();
const mapLoading = ref(false);
const activePoint = ref();
const showMultiPointPopup = ref(false);
const features = ref([]);
const allFeatures = ref([]);
const allQueriedPoints = ref();
const featuresUnderCursor = ref([]);
const groundWaterPoints = ref();
const pointsLoading = ref(false);
const marker = ref();
const reportOpen = ref(false);
const reportData = ref([]);
const groundWaterSearchableProperties = [
    { label: 'Station Name', type: 'stationName', property: 'name' },
    { label: 'Station ID', type: 'stationId', property: 'id' }
];
const groundWaterFilters = ref({
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
        network: [],
    },
});

const pointCount = computed(() => {
    if(groundWaterPoints.value) {
        return groundWaterPoints.value.features.length;
    };
    return 0;
});

const getReportData = async () => {
    mapLoading.value = true;
    reportData.value = await getGroundWaterQualityReportById(activePoint.value.id);
    reportOpen.value = true;
    mapLoading.value = false;
}

/**
 * 
 * @param coords Array of lng, lat coordinates to place the marker
 */
const createMarker = (coords) => {
    if(marker.value){
        marker.value.remove();
    };
    marker.value = new mapboxgl.Marker()
        .setLngLat({ lng: coords[0], lat: coords[1]})
        .addTo(map.value)
}

/**
 * Add Watershed License points to the supplied map
 * @param mapObj Mapbox Map
 */
 const loadPoints = async (mapObj) => {
    mapLoading.value = true;
    pointsLoading.value = true;
    map.value = mapObj;
    groundWaterPoints.value = await getGroundWaterQualityStations();

    if (!map.value.getSource("point-source")) {
        const featureJson = {
            type: "geojson",
            data: groundWaterPoints.value,
        };
        allFeatures.value = groundWaterPoints.value.features;
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
        if(marker.value) marker.value.remove();
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
        // in this case, ensure the multiple point popup is closed
    }
    showMultiPointPopup.value = false;
};

/**
 * Gets the licenses currently in the viewport of the map
 */
 const getVisibleLicenses = (isFiltered = false) => {
    pointsLoading.value = true;
    allQueriedPoints.value = groundWaterPoints.value.features;
    if (map.value.getZoom() >= 9 && !isFiltered) {
        const queriedFeatures = map.value.queryRenderedFeatures({
            layers: ["point-layer"],
        });
        allQueriedPoints.value = queriedFeatures;
    }
    pointsLoading.value = false;
    return allQueriedPoints.value
};

/**
 * Receive changes to filters from MapFilters component and apply filters to the map
 * @param newFilters Filters passed from MapFilters
 */
 const updateFilters = (newFilters) => {
    groundWaterFilters.value = newFilters;
    const mapFilter = buildFilteringExpressions(newFilters);
    map.value.setFilter("point-layer", mapFilter);
    pointsLoading.value = true;
    setTimeout(() => {
        features.value = getVisibleLicenses(true);
        const selectedFeature = features.value.find(
            (feature) => feature.properties.id === activePoint.value?.id
        );
        if (selectedFeature === undefined) dismissPopup();
        pointsLoading.value = false;
    }, 500);
};

const downloadSelectedPointData = async () => {
    await downloadGroundwaterQualityCSV(activePoint.value.id)
};

/**
 * Dismiss the map popup and clear the highlight layer
 */
const dismissPopup = () => {
    activePoint.value = null;
    map.value.setFilter("highlight-layer", false);
};
</script>
