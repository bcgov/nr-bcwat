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
                    title="Water Allocations"
                    paragraph="Points on the map represent existing water allocations. Control what is shown using the check boxes and filters below,
                        and click on a marker on the map, or an entry in the list below to get more details. To generate a watershed report, click on any stream, river, or lake."
                    :all-points="points"
                    :loading="pointsLoading"
                    :points-to-show="features"
                    :active-point-id="activePoint?.id"
                    :total-point-count="pointCount"
                    :filters="watershedFilters"
                    page="watershed"
                    :view-more="false"
                    :has-flow-quantity="true"
                    :view-extent-on="map?.getZoom() < 9"
                    @update-filter="(newFilters) => updateFilters(newFilters)"
                    @select-point="(point) => selectPoint(point)"
                />
                <div class="map-container">
                    <MapSearch
                        v-if="allFeatures.length > 0 && watershedSearchableProperties.length > 0"
                        :map="map"
                        :map-points-data="allFeatures"
                        :searchable-properties="watershedSearchableProperties"
                        @select-point="(point) => activePoint = point.properties"
                        @select-watershed="wfi => getWatershedInfoByWFI(wfi)"
                        @go-to-location="(coordinates) => clickMap(coordinates)"
                        @place-marker="createMarker"
                    />
                    <Map
                        current-section="watershed"
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
                                    @loading="!reportContent"
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
                @close="reportOpen = false; reportContent = null;"
            />
        </div>
    </div>
</template>

<script setup>
import { bbox } from '@turf/bbox';
import Map from "@/components/Map.vue";
import MapSearch from "@/components/MapSearch.vue";
import MapFilters from "@/components/MapFilters.vue";
import MapPointSelector from "@/components/MapPointSelector.vue";
import WatershedReport from "@/components/watershed/WatershedReport.vue";
import mapboxgl from 'mapbox-gl';
import { buildFilteringExpressions } from '@/utils/mapHelpers.js';
import { getAllWatershedLicences, getWatershedByLatLng, getWatershedReportByWFI, getWatershedByWFI } from '@/utils/api.js';
import { highlightLayer, pointLayer } from "@/constants/mapLayers.js";
import { computed, ref } from "vue";

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
const features = ref([]);
const marker = ref();
const firstSymbolId = ref();
const allFeatures = ref([]);
const allQueriedPoints = ref();
const featuresUnderCursor = ref([]);
// page-specific data search handlers
const watershedSearchableProperties = [
    { label: 'Licence Number', type: 'licence', property: 'nid' },
    { label: 'Watershed Feature Id', type: 'watershed-feature', property: 'wfi' },
];
const watershedFilters = ref({
    buttons: [
        {
            value: true,
            label: "Surface Water",
            color: "green-1",
            // TODO the key `st` is temporary, should be replaced with `status` in future.
            key: "type",
            matches: [
                'SW'
            ]
        },
        {
            value: true,
            label: "Ground Water",
            color: "blue-1",
            // TODO the key `st` is temporary, should be replaced with `status` in future.
            key: "type",
            matches: [
                'GW'
            ]
        },
    ],
    other: {
        term: [
            {
                label: 'Long',
                key: 'term',
                value: true,
                matches: 'long'
            },
            {
                label: 'Short',
                key: 'term',
                value: true,
                matches: 'short'
            }
        ],
        status: [
            {
                label: "Active Appl.",
                matches: "ACTIVE APPL.",
                value: true,
                key: 'st'
            },
            {
                label: "Current",
                matches: "CURRENT",
                value: true,
                key: 'st'
            },
        ],
        industry: [
            {
                label: "Commercial",
                value: true,
                key: 'ind',
                matches: "Commercial"
            },
            {
                label: "Agriculture",
                value: true,
                key: 'ind',
                matches: "Agriculture"
            },
            {
                label: "Municipal",
                value: true,
                key: 'ind',
                matches: "Municipal"
            },
            {
                label: "Other",
                value: true,
                key: 'ind',
                matches: "Other"
            },
            {
                label: "Power",
                value: true,
                key: 'ind',
                matches: "Power"
            },
            {
                label: "Oil & Gas",
                value: true,
                key: 'ind',
                matches: "Oil & Gas"
            },
        ],
        // @TODO: Add new network values requested from UAT
        network: []
    },
});

const pointCount = computed(() => {
    if (points.value) return points.value.length;
    return 0;
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
    }
    if (!map.value.getLayer("highlight-layer")) {
        map.value.addLayer(highlightLayer, "poi-islands");
    }

    map.value.on("click", async (ev) => {
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
                activePoint.value = point[0].properties;
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

    map.value.on("movestart", () => {
        if (map.value.getZoom() > 9) pointsLoading.value = true;
    });

    map.value.on("moveend", () => {
        features.value = getVisibleLicenses();
    });

    map.value.once("idle", () => {
        features.value = getVisibleLicenses();
    });
    loading.value = false;
};

/**
 * Triggers a map click at the selected coordinates from search result
 *
 * @param coordinates - array of lng/lat coordinates to be used by mapbox
 */
const clickMap = (coordinates) => {
    getWatershedInfoAtLngLat({lng: coordinates[0], lat: coordinates[1]});
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
                        'fill-color': 'orange',
                        'fill-opacity': 0.6
                    }
                }, firstSymbolId.value);
            }
        } catch(e) {
            console.error('unable to set watershed polygon');
        }
    }
    loading.value = false;
};

const goToLocation = (polygon) => {
    const boundingBox = bbox(polygon);
    map.value.fitBounds(boundingBox, { padding: 50 });
};

const openReport = async () => {
    loading.value = true;
    loadingMsg.value = "Loading report data. Please wait..."
    reportContent.value = await getWatershedReportByWFI(watershedInfo.value.wfi);
    loading.value = false;
    if (reportContent.value) {

        // The below lines of code address an issue with lakes, the watershed report is generated for the upstream most point of the stream that flows out of the lake but the report is still meant to represent the lake. Therefore, we set the watershed name in the report overview to be the name of the lake instead of the river it was generated for. We also ensure that the lake name is included in the bus stop names for the report (the if statement is to not double add it for the normal case on rivers where it is already included).
        reportContent.value.overview.watershedName = watershedInfo.value.name;
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
    // Not sure if updating these here matters, the emitted filter is what gets used by the map
    watershedFilters.value = newFilters;
    const mapFilter = buildFilteringExpressions(newFilters);
    map.value.setFilter("point-layer", mapFilter);
    pointsLoading.value = true;

    setTimeout(() => {
        features.value = getVisibleLicenses(true);
        const selectedFeature = features.value.find((feature) => feature.properties.id === activePoint.value?.id);
        if (selectedFeature === undefined) dismissPopup();
    }, 500);
};

/**
 * Receive a point from the map filters component and highlight it on screen
 * @param newPoint Selected Point
 */
const selectPoint = (newPoint) => {
    if (newPoint) {
        map.value.setFilter("highlight-layer", ["==", "id", newPoint.id]);
        activePoint.value = newPoint;
    }
    showMultiPointPopup.value = false;
};

/**
 * fetches only those uniquely-id'd features within the current map view
 */
const getVisibleLicenses = (isFiltered = false) => {
    // If we've already queried all points, only run query again when zoomed in past level 9
    if (allQueriedPoints.value && map.value.getZoom() < 9 && !isFiltered) {
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
