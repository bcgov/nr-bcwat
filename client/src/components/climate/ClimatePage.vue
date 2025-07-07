<template>
    <div>
        <div class="page-container">
            <MapFilters
                title="Climate Stations"
                :loading="pointsLoading"
                :points-to-show="features"
                :active-point-id="`${activePoint?.id}`"
                :total-point-count="pointCount"
                :filters="climateFilters"
                @update-filter="(newFilters) => updateFilters(newFilters)"
                @select-point="(point) => selectPoint(point)"
                @view-more="getReportData"
            />
            <div class="map-container">
                <MapSearch 
                    v-if="allFeatures.length > 0 && climateSearchableProperties.length > 0"
                    :map="map"
                    :map-points-data="allFeatures"
                    :searchable-properties="climateSearchableProperties"
                    @select-point="(point) => activePoint = point.properties"
                />
                <Map 
                    :loading="mapLoading"
                    @loaded="(map) => loadPoints(map)" 
                />
                <MapPointSelector 
                    :points="featuresUnderCursor"
                    :open="showMultiPointPopup"
                    @close="(point) => {
                        if(point){
                            selectPoint(point)
                        }
                    }"
                />
            </div>
        </div>
        <ClimateReport
            v-if="activePoint && reportData"
            :report-open="reportOpen"
            :report-content="reportData"
            :active-point="activePoint"
            @close="
                dismissPopup();
                reportOpen = false;
                activePoint = null;
            "
        />
    </div>
</template>

<script setup>
import Map from "@/components/Map.vue";
import MapSearch from '@/components/MapSearch.vue';
import MapFilters from "@/components/MapFilters.vue";
import MapPointSelector from '@/components/MapPointSelector.vue';
import ClimateReport from "@/components/climate/ClimateReport.vue";
import { highlightLayer, pointLayer } from "@/constants/mapLayers.js";
import { getClimateStations, getClimateReportById } from '@/utils/api.js';
import { computed, ref } from "vue";

const map = ref();
const mapLoading = ref(false);
const points = ref();
const pointsLoading = ref(false);
const activePoint = ref();
const reportOpen = ref(false);
const reportData = ref();
const showMultiPointPopup = ref(false);
const features = ref([]);
const allFeatures = ref([]);
const featuresUnderCursor = ref([]);
// page-specific data search handlers
const climateSearchableProperties = [
    { label: 'Station Name', type: 'stationName', property: 'name' },
    { label: 'Station ID', type: 'stationId', property: 'id' }
];
const climateFilters = ref({
    buttons: [
        {
            value: true,
            label: "Historical Data",
            color: "blue-4",
        },
        {
            value: true,
            label: "Current Data",
            color: "orange-6",
        },
    ],
    other: {
        network: [
            {
                value: true,
                label: "Agriculture and Rural Development ACt Network",
            },
            {
                value: true,
                label: "BC ENV - Air Quality Network",
            },
            {
                value: true,
                label: "BC ENV - Automated Snow Pillow Network",
            },
            {
                value: true,
                label: "BC ENV - Manual Snow Survey",
            },
            {
                value: true,
                label: "BC ENV - Real-time Water Data",
            },
            {
                value: true,
                label: "BC FLNRORD - Wild Fire Management Branch",
            },
            {
                value: true,
                label: "BC Hydro",
            },
            {
                value: true,
                label: "BC Ministry of Agriculture",
            },
            {
                value: true,
                label: "BC MoTI",
            },
            {
                value: true,
                label: "Coastal Hydrology & Climate Change Research Lab / BC FLNRORD - Forest Ecosystems Research Network",
            },
            {
                value: true,
                label: "Environment Canada",
            },
            {
                value: true,
                label: "Forest Renewal British Columbia",
            },
        ],
        analyses: [
            {
                value: true,
                label: "Manual Snow Pillow Water Equivalent",
            },
            {
                value: true,
                label: "Precipitation Amount",
            },
            {
                value: true,
                label: "Snow Water Equivalent",
            },
            {
                value: true,
                label: "Surface Snow Depth (Point)",
            },
            {
                value: true,
                label: "Temperature (Max.)",
            },
            {
                value: true,
                label: "Temperature (Mean.)",
            },
            {
                value: true,
                label: "Temperature (Min.)",
            },
        ],
        status: [
            {
                value: true,
                label: "Current",
            },
            {
                value: true,
                label: "Historical",
            },
        ],
    },
});

const pointCount = computed(() => { 
    if(points.value) return points.value.length; 
    return 0;
})

/**
 * Add climate License points to the supplied map
 * @param mapObj Mapbox Map
 */
const loadPoints = async (mapObj) => {
    mapLoading.value = true;
    map.value = mapObj;
    points.value = await getClimateStations();
    
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
            ["get", "ty"],
            0,
            "#42a5f5",
            1,
            "#f06825",
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

    map.value.once("idle", () => {
        features.value = getVisibleLicenses();
        pointsLoading.value = false;
    });

    mapLoading.value = false;
};

const getReportData = async () => {
    mapLoading.value = true;
    reportData.value = await getClimateReportById(activePoint.value.id);
    reportOpen.value = true;
    mapLoading.value = false;
}

/**
 * Receive changes to filters from MapFilters component and apply filters to the map
 * @param newFilters Filters passed from MapFilters
 */
const updateFilters = (newFilters) => {
    // Not sure if updating these here matters, the emitted filter is what gets used by the map
    climateFilters.value = newFilters;

    const mapFilter = ["any"];

    if (
        newFilters.buttons.find((filter) => filter.label === "Historical Data")
            .value
    ) {
        mapFilter.push(["==", "ty", 0]);
    }
    if (
        newFilters.buttons.find((filter) => filter.label === "Current Data")
            .value
    ) {
        mapFilter.push(["==", "ty", 1]);
    }

    map.value.setFilter("point-layer", mapFilter);
    // Without the timeout this function gets called before the map has time to update
    pointsLoading.value = true;
    setTimeout(() => {
        features.value = getVisibleLicenses();
        const myFeat = features.value.find(
            (feature) => feature.properties.id === activePoint.value?.id
        );
        if (myFeat === undefined) dismissPopup();
        pointsLoading.value = false;
    }, 500);
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
        if(showMultiPointPopup.value){
            showMultiPointPopup.value = false;
        }
    } else {
        // in this case, ensure the multiple point popup is closed 
        if(showMultiPointPopup.value){
            showMultiPointPopup.value = false;
        }
    }
};
/**
 * fetches only those uniquely-id'd features within the current map view
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
        const id = feature.properties["id"];
        if (!uniqueIds.has(id)) {
            uniqueIds.add(id);
            uniqueFeatures.push(feature);
        }
    }
    return uniqueFeatures;
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
