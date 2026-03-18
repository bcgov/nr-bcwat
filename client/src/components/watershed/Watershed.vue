<template>
    <div>
        <div
            v-if="loading"
            class="loader-container"
        >
            <q-spinner
                class="map-loader"
                size="xl"
            />
            <div>
                {{ loadingMsg }}
            </div>
        </div>
        <div>
            <div class="page-container">
                <MapFilters
                    title="Watershed"
                    points-name="Allocations"
                    paragraph="Points on the map represent existing water allocations. Control what is shown using the check boxes and filters below,
                        and click on a marker on the map, or an entry in the list below to get more details. To generate a watershed report, click on any stream, river, or lake."
                    :all-points="points"
                    :loading="pointsLoading"
                    :points-to-show="sidebarFeatures"
                    :selected-point-from-map="activePoint"
                    :filterable-properties="filterableProperties"
                    :map="map"
                    :total-point-count="pointCount"
                    page="watershed"
                    :view-more="false"
                    :has-flow-quantity="true"
                    @update-filter="(newFilters) => updateFilters(newFilters)"
                    @select-point="(point) => selectPoint(point)"
                />
                <div class="map-container">
                    <MapSearch
                        v-if="map && allFeatures.length > 0 && watershedSearchableProperties.length > 0"
                        :map="map"
                        :map-points-data="allFeatures"
                        :searchable-properties="watershedSearchableProperties"
                        @select-point="(point) => getWatershedFromLngLat(point)"
                        @select-watershed="wfi => getWatershedInfoByWFI(wfi)"
                        @go-to-location="(coordinates) => clickMap(coordinates)"
                        @place-marker="createMarker"
                    />
                    <Map
                        current-section="watershed"
                        :preserve-drawing-buffer="true"
                        @loaded="(map) => loadPoints(map)"
                    />
                    <q-card
                        v-if="watershedInfo"
                        class="watershed-info-popup"
                        color="primary"
                    >
                        <q-card-section class="bg-primary text-white">
                            <div class="watershed-info-header">
                                <div class="text-h5 ">
                                    {{ watershedInfo.name }}
                                    <q-btn
                                        icon="mdi-map-marker"
                                        flat
                                        @click="goToLocation(watershedPolygon)"
                                    >
                                        <q-tooltip>
                                            Zoom to watershed extent
                                        </q-tooltip>
                                    </q-btn>
                                </div>
                                <q-btn
                                    flat
                                    icon="close"
                                    @click="closeWatershedInfo"
                                />
                            </div>
                            <div class="text-body2">WFI: {{ watershedInfo.wfi }}</div>
                        </q-card-section>
                        <q-card-section>
                            <div class="text-center">
                                <q-btn
                                    color="primary"
                                    data-cy="view-report-button"
                                    @loading="!reportReady"
                                    @click="openReport"
                                    label="view report"
                                />
                            </div>
                        </q-card-section>
                    </q-card>
                    <MapPointSelector
                        :points="featuresUnderCursor"
                        :open="showMultiPointPopup"
                        @close="selectPoint"
                    />
                </div>
            </div>
            <WatershedReport
                v-if="clickedPoint && reportContent"
                :report-open="reportOpen"
                :report-content="reportContent"
                :clicked-point="clickedPoint"
                :points="points"
                :wfi="watershedInfo.wfi"
                @close="reportOpen = false; reportContent = null;"
            />
        </div>
    </div>
</template>

<script setup>
import Map from "@/components/Map.vue";
import MapSearch from "@/components/MapSearch.vue";
import MapFilters from "@/components/MapFilters.vue";
import MapPointSelector from "@/components/MapPointSelector.vue";
import WatershedReport from "@/components/watershed/WatershedReport.vue";
import mapboxgl from 'mapbox-gl';
import { 
    getFilteredPoints,
    goToLocation
} from '@/utils/mapHelpers.js';
import { getAllWatershedLicences, getWatershedByLatLng, getWatershedReportByWFI, getWatershedByWFI } from '@/utils/api.js';
import { highlightLayer, pointLayer } from "@/constants/mapLayers.js";
import { computed, onBeforeUnmount, ref } from "vue";

const map = ref();
const points = ref();
const pointsLoading = ref(false);
const loading = ref(false);
const loadingMsg = ref('Loading points. Please wait...');
const reportContent = ref(null);
const activePoint = ref();
const clickedPoint = ref(null);
const showMultiPointPopup = ref(false);
const watershedInfo = ref(null);
const watershedPolygon = ref(null);
const reportOpen = ref(false);
const reportReady = ref(false);
const sidebarFeatures = ref([]);
const filteredFeatures = ref();
const filterableProperties = ref({});
const marker = ref();
const matchFilters = ref();
const uniqueFilters = ref();
const selectedWatershedCanvas = ref();
const firstSymbolId = ref();
const allFeatures = ref([]);
const allQueriedPoints = ref();
const featuresUnderCursor = ref([]);
// page-specific data search handlers
const watershedSearchableProperties = [
    { label: 'Licence Number', type: 'licence', property: 'nid' },
    { label: 'Watershed Feature Id', type: 'watershed-feature', property: 'wfi' },
];

const pointCount = computed(() => {
    if (points.value) return points.value.length;
    return 0;
});

onBeforeUnmount(() => {
    map.value.remove();
});

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
    loading.value = true;
    loadingMsg.value = "Loading points. Please wait..."
    pointsLoading.value = true;
    map.value = mapObj;

    const layers = map.value.getStyle().layers;
    for (const layer of layers) {
        if (layer.type === 'symbol') {
            firstSymbolId.value = layer.id;
            break;
        }
    }

    points.value = await getAllWatershedLicences();
    filteredFeatures.value = points.value.features;
    sidebarFeatures.value = getVisibleLicenses(filteredFeatures.value);
    // NOTE: we could modify the points response object to have a dynamic list of 
    // filterable properties, and set all the relevant filters using that list.
    filterableProperties.value = getFilterableProperties();

    if (!map.value.getSource("point-source")) {
        const featureJson = {
            type: "geojson",
            data: points.value,
        };
        allFeatures.value = points.value.features;
        map.value.addSource("point-source", featureJson);
    }
    if (!map.value.getLayer("point-layer")) {
        map.value.addLayer(pointLayer, "poi-islands");
        map.value.setPaintProperty("point-layer", "circle-color", [
            "match",
            ["get", "type"],
            "SW",
            "#61913d",
            "GW",
            "#234075",
            "#ccc",
        ]);
        map.value.setPaintProperty("point-layer", "circle-stroke-color", [
            "match",
            ["get", "st"],
            "ACTIVE APPL.",
            "#FAA500",
            "#fff",
        ]);
    }
    if (!map.value.getLayer("highlight-layer")) {
        map.value.addLayer(highlightLayer, "poi-islands");
    }

    map.value.on("click", async (ev) => {
        if(marker.value) marker.value.remove();
        watershedInfo.value = null;
        const point = map.value.queryRenderedFeatures(ev.point, {
            layers: ["point-layer"],
        });

        if (point.length) {
            if (point.length === 1) {
                map.value.setFilter("highlight-layer", [
                    "==",
                    "id",
                    point[0].properties.id,
                ]);
                point[0].properties.id = point[0].properties.id.toString();
                activePoint.value = point[0];
                activePoint.value.id = point[0].properties.id;
            }
            if (point.length > 1) {
                featuresUnderCursor.value = point;
                showMultiPointPopup.value = true;
            }
        } else {
            clickedPoint.value = ev.lngLat;
            // TODO: Make api call here to fetch watershed polygon for lat/lng
            // and generate the report.
            getWatershedInfoAtLngLat(ev.lngLat)
        }
    });

    map.value.on("mouseenter", "point-layer", () => {
        map.value.getCanvas().style.cursor = "pointer";
    });

    map.value.on("mouseleave", "point-layer", () => {
        map.value.getCanvas().style.cursor = "";
    });

    map.value.on("moveend", () => {
        sidebarFeatures.value = getVisibleLicenses(filteredFeatures.value);
    });

    map.value.once("idle", () => {
        sidebarFeatures.value = getVisibleLicenses(filteredFeatures.value);
    });

    loading.value = false;
};

/**
 * Triggers a map click at the selected coordinates from search result
 *
 * @param coordinates - array of lng/lat coordinates to be used by mapbox
 */
const clickMap = (coordinates) => {
    if(marker.value) marker.value.remove();
    getWatershedInfoAtLngLat({lng: coordinates[0], lat: coordinates[1]});
};

const getWatershedFromLngLat = (point) => {
    activePoint.value = [point[1], point[0]];
    clickedPoint.value = { lng: point[1], lat: point[0] };
    getWatershedInfoAtLngLat({lng: activePoint.value[0], lat: activePoint.value[1]});
};

const getWatershedInfoAtLngLat = async (coordinates) => {
    loading.value = true;
    loadingMsg.value = "Loading Watershed. Please wait..."
    watershedInfo.value = await getWatershedByLatLng(coordinates);
    getWatershedInfo();
};

const getWatershedInfoByWFI = async (wfi) => {
    loading.value = true;
    loadingMsg.value = "Loading Watershed. Please wait..."
    watershedInfo.value = await getWatershedByWFI(wfi);
    clickedPoint.value = { lng: watershedInfo.value.geojson.coordinates[0][0][0], lat: watershedInfo.value.geojson.coordinates[0][0][1] };
    getWatershedInfo();
};

const getWatershedInfo = async () => {
    if (watershedInfo.value && 'geojson' in watershedInfo.value) {
        watershedPolygon.value = watershedInfo.value.geojson;
        try {
            if (map.value.getSource('watershed-polygon-source')) {
                map.value.getSource('watershed-polygon-source').setData(watershedInfo.value.geojson);
            } else {
                map.value.addSource('watershed-polygon-source', {
                    type: 'geojson',
                    data: watershedInfo.value.geojson
                });
            }

            if (!map.value.getLayer('watershed-polygon-layer')) {
                map.value.addLayer({
                    'id': 'watershed-polygon-layer',
                    'source': 'watershed-polygon-source',
                    'type': 'fill',
                    'paint': {
                        'fill-color': 'orangered',
                        'fill-opacity': 0.4
                    }
                }, firstSymbolId.value);
            }

            goToLocation(watershedPolygon.value, map.value)
        } catch(e) {
            console.error('unable to set watershed polygon');
        }
    }
    loading.value = false;
};

const openReport = async () => {
    loading.value = true;
    loadingMsg.value = "Loading report data. Please wait..."
    selectedWatershedCanvas.value = map.value.getCanvas().toDataURL('image/png');
    reportContent.value = await getWatershedReportByWFI(watershedInfo.value.wfi);
    loading.value = false;
    if (reportContent.value) {

        // The below lines of code address an issue with lakes, the watershed report is generated for the upstream most point of the stream that flows out of the lake but the report is still meant to represent the lake. Therefore, we set the watershed name in the report overview to be the name of the lake instead of the river it was generated for. We also ensure that the lake name is included in the bus stop names for the report (the if statement is to not double add it for the normal case on rivers where it is already included).
        reportContent.value.overview.watershedName = watershedInfo.value.name;
        reportContent.value.overview.watershedImg = selectedWatershedCanvas.value || '';
        if (!reportContent.value.overview.busStopNames.includes(watershedInfo.value.name)) {
            reportContent.value.overview.busStopNames.unshift(watershedInfo.value.name);
        }
        if (reportContent.value.overview.watershedName.trim() === reportContent.value.overview.mgmt_name.trim()) {
            reportContent.value.overview.mgmt_name += " (Downstream)";
        }

        reportOpen.value = true;
    }
};

/**
 * Receive changes to filters from MapFilters component and apply filters to the map
 * @param newFilters Filters passed from MapFilters
 */
const updateFilters = (newFilters) => {
    // set the filtering
    pointsLoading.value = true;

    // set the filters
    // [ matchFilters.value, uniqueFilters.value ] = setPointFilters(newFilters);

    // set the current map features based on what is visible and filtered out
    filteredFeatures.value = getFilteredPoints(points.value.features, newFilters.matchFilters, newFilters.uniqueFilters);

    // update the map source with the new filtered points
    if(map.value.getSource('point-source')) {
        map.value.getSource('point-source').setData({
            type: "FeatureCollection",
            features: filteredFeatures.value
        });
    }

    sidebarFeatures.value = getVisibleLicenses(filteredFeatures.value);
    
    // small check to determine if a feature was selected, if so close the popup
    const selectedFeature = filteredFeatures.value.find((feature) => feature.properties.id === activePoint.value?.properties.id);
    if (!selectedFeature) dismissPopup();
    pointsLoading.value = false;
};

/**
 * Receive a point from the map filters component and highlight it on screen
 * @param newPoint Selected Point
 */
const selectPoint = (newPoint) => {
    if (newPoint?.properties?.id) {
        map.value.setFilter("highlight-layer", ["==", "id", newPoint.properties.id]);
        activePoint.value = newPoint;
    }
    showMultiPointPopup.value = false;
};

/**
 * fetches only those uniquely-id'd features within the current map view
 */
const getVisibleLicenses = (features) => {
    pointsLoading.value = true;

    const bounds = map.value.getBounds();

    const queriedFeatures = features.filter(pointFeature => {
        // Extract the coordinates from the point feature (adjust based on your data structure)
        const coordinates = pointFeature.geometry.coordinates;
        const lngLat = new mapboxgl.LngLat(coordinates[0], coordinates[1]);

        // Check if the point is within the current bounds
        return bounds.contains(lngLat);
    });

    const uniqueIds = new Set();
    const uniqueFeatures = [];
    for (const feature of queriedFeatures) {
        const id = feature.properties["id"];
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

const closeWatershedInfo = () => {
    watershedInfo.value = null;
    map.value.removeLayer('watershed-polygon-layer');
    map.value.removeSource('watershed-polygon-source');
};

/**
 * Dismiss the map popup and clear the highlight layer
 */
const dismissPopup = () => {
    activePoint.value = null;
    map.value.setFilter("highlight-layer", false);
};

const getFilterableProperties = () => {
    const filterablePropertiesObj = {
        "matchFilters": [
            {
                "category": "Term",
                "filters": [
                    {
                        "label": "Long",
                        "matchValue": "long",
                        "property": "term"
                    },
                    {
                        "label": "Short",
                        "matchValue": "short",
                        "property": "term"
                    }
                ]
            },
            {
                "category": "Type",
                "filters": [
                    {
                        "label": "Ground Water",
                        "matchValue": "GW",
                        "property": "type"
                    },
                    {
                        "label": "Surface Water",
                        "matchValue": "SW",
                        "property": "type"
                    }
                ]
            },
            {
                "category": "Network",
                "filters": [
                    {
                        "label": "BC Ministry of Forests",
                        "matchValue": "BC Ministry of Forests",
                        "property": "net"
                    },
                    {
                        "label": "ERAA",
                        "matchValue": "ERAA",
                        "property": "net"
                    },
                    {
                        "label": "Canada Energy Regulator",
                        "matchValue": "Canada Energy Regulator",
                        "property": "net"
                    }
                ]
            },
            {
                "category": "Industry",
                "filters": [
                    {
                        "label": "Other",
                        "matchValue": "Other",
                        "property": "ind"
                    },
                    {
                        "label": "Agriculture",
                        "matchValue": "Agriculture",
                        "property": "ind"
                    },
                    {
                        "label": "Power",
                        "matchValue": "Power",
                        "property": "ind"
                    },
                    {
                        "label": "Commercial",
                        "matchValue": "Commercial",
                        "property": "ind"
                    },
                    {
                        "label": "Municipal",
                        "matchValue": "Municipal",
                        "property": "ind"
                    },
                    {
                        "label": "Oil & Gas",
                        "matchValue": "Oil & Gas",
                        "property": "ind"
                    }
                ]
            },
            {
                "category": "Status",
                "filters": [
                    {
                        "label": "Current",
                        "matchValue": "CURRENT",
                        "property": "st"
                    },
                    {
                        "label": "Active Application",
                        "matchValue": "ACTIVE APPL.",
                        "property": "st"
                    }
                ]
            }
        ],
        "uniqueFilters": {
            "hasArea": false,
            "hasQuantity": true,
            "hasYearRange": false
        }
    }

    return filterablePropertiesObj;
}
</script>

<style lang="scss" scoped>
.point-info {
    background-color: black;
}

.watershed-info-popup {
    position: absolute;
    height: fit-content;
    width: 400px;
    left: 33%;
    bottom: 1rem;

    .watershed-info-header {
        display: flex;
        justify-content: space-between;
    }
}
</style>
