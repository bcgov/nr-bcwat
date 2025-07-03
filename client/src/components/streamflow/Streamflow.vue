<template>
    <div>
        <div class="page-container">
            <MapFilters
                title="Water Allocations"
                :loading="pointsLoading"
                :points-to-show="features"
                :active-point-id="activePoint?.id.toString()"
                :total-point-count="pointCount"
                :filters="streamflowFilters"
                @update-filter="(newFilters) => updateFilters(newFilters)"
                @select-point="(point) => selectPoint(point)"
                @view-more="getReportData()"
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
                    :loading="mapLoading"
                    @loaded="(map) => loadPoints(map)" 
                />
                <MapPointSelector 
                    :points="featuresUnderCursor"
                    :open="showMultiPointPopup"
                    @close="(point) => selectPoint(point)"
                />
            </div>
        </div>
        <StreamflowReport
            :active-point="activePoint"
            :report-open="reportOpen"
            :report-data="reportData"
            @close="reportOpen = false"
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
import { getStreamflowAllocations, getStreamflowReportDataById } from '@/utils/api.js';
import StreamflowReport from "./StreamflowReport.vue";

const map = ref();
const activePoint = ref();
const showMultiPointPopup = ref(false);
const featuresUnderCursor = ref([]);
const points = ref();
const allFeatures = ref([]);
const features = ref([]);
const mapLoading = ref(false);
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
            label: "Historical data",
            color: "green-1",
        },
        {
            value: true,
            label: "Current data",
            color: "green-1",
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
    points.value = await getStreamflowAllocations();

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

        
        allFeatures.value.forEach(el => {
            if(el.properties.net !== 1){
                console.log(el)
            }
        })
        
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

    const mapFilter = ["any"];
    map.value.setFilter("point-layer", mapFilter);
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
