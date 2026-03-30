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
                    :title="currentPageText.title"
                    points-name="Stations"
                    :paragraph="currentPageText.paragraph"
                    :all-points="points"
                    :loading="pointsLoading"
                    :points-to-show="sidebarFeatures"
                    :selected-point-from-map="activePoint"
                    :map="map"
                    :total-point-count="pointCount"
                    :filterable-properties="filterableProperties"
                    page="water-portal"
                    :view-more="true"
                    :view-extent-on="map?.getZoom() < 9"
                    @update-filter="updateFilters"
                    @select-point="selectPoint"
                    @view-more="getReportForPoint"
                    @download-data="downloadCSV"
                />
                <div class="map-container">
                    <MapSearch
                        v-if="map && allFeatures && allFeatures.length > 0 && waterPortalSearchableProperties && waterPortalSearchableProperties.length > 0"
                        :map="map"
                        :map-points-data="allFeatures"
                        :searchable-properties="waterPortalSearchableProperties"
                        @go-to-location="(coordinates) => clickMap(coordinates)"
                        @geolocate="geolocate"
                        @place-marker="(coords) => {
                            marker = createMarker(marker, map, coords)
                        }"
                    />
                    <Map
                        @loaded="(map) => loadPoints(map)"
                    />
                    <MapPointSelector
                        :points="featuresUnderCursor"
                        :open="showMultiPointPopup"
                        page="waterportal"
                        @close="selectPoint"
                    />
                    <StreamflowReport
                        v-if="reportData && showReport && props.defaultViewType === 'streams'"
                        :active-point="activePoint.properties"
                        :report-open="showReport"
                        :report-data="reportData"
                        @close="closeReport"
                    />
                    <WaterQualityReport
                        v-if="reportData && showReport && props.defaultViewType === 'surface'"
                        :active-point="activePoint.properties"
                        :report-type="'Surface'"
                        :chemistry="reportData"
                        :report-open="showReport"
                        @close="closeReport"
                    />
                    <WaterQualityReport
                        v-if="reportData && showReport && props.defaultViewType === 'ground'"
                        :active-point="activePoint.properties"
                        :report-type="'Ground'"
                        :chemistry="reportData"
                        :report-open="showReport"
                        @close="closeReport"
                    />
                    <GroundWaterLevelReport
                        v-if="reportData && showReport && props.defaultViewType === 'wells'"
                        :active-point="activePoint.properties"
                        :report-data="reportData"
                        :report-open="showReport"
                        :report-type="'Ground Water'"
                        @close="closeReport"
                    />
                    <ClimateReport
                        v-if="reportData && showReport && props.defaultViewType === 'climate'"
                        :report-open="showReport"
                        :report-content="reportData"
                        :active-point="activePoint.properties"
                        @close="closeReport"
                    />
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import Map from '@/components/Map.vue';
import MapFilters from '@/components/MapFilters.vue';
import MapSearch from '@/components/MapSearch.vue';
import MapPointSelector from '@/components/MapPointSelector.vue';
import StreamflowReport from '@/components/streamflow/StreamflowReport.vue';
import WaterQualityReport from '@/components/waterquality/WaterQualityReport.vue';
import GroundWaterLevelReport from "@/components/groundwater-level/GroundWaterLevelReport.vue";
import ClimateReport from '@/components/climate/ClimateReport.vue';
import maplibregl from 'mapbox-gl';
import {
    fetchCache,
    portalHandler
} from '@/utils/reactor.js';
import {
    geolocate,
    getFilteredPoints,
    createMarker,
    getFilterablePropertiesByViewType
} from '@/utils/mapHelpers.js';
import { highlightLayer, pointLayer } from "@/constants/mapLayers.js";
import {
    getWaterPortalReportDataByIdAndType,
    downloadCSVByTypeAndId,
} from '@/utils/api.js';
import { useRoute } from 'vue-router';
import { computed, onMounted, ref, watch } from 'vue';
import { Notify } from 'quasar';

const route = useRoute();

// page-specific data search handlers
const waterPortalSearchableProperties = [
    { label: 'UTM', type: 'utm', property: 'utm' },
    { label: 'Watershed Feature Id', type: 'watershed-feature', property: 'wfi' },
];

watch(() => portalHandler.viewType, async (newViewType, oldViewType) => {
    if (oldViewType !== '') await onViewTypeUpdate(newViewType);
});

const props = defineProps({
    defaultViewType: {
        type: String,
        default: 'streams',
        required: true
    }
});

const map = ref(null);
const points = ref([]);
const pointsLoading = ref(false);
const activePoint = ref(null);
const loading = ref(false);
const loadingMsg = ref('Loading. Please wait...');
const allFeatures = ref([]);
const sidebarFeatures = ref([]);
const filteredFeatures = ref([]);
const featuresUnderCursor = ref([]);
const showMultiPointPopup = ref(false);
const showReport = ref(false);
const firstSymbolId = ref();
const allQueriedPoints = ref([]);
const marker = ref(null);
const reportData = ref(null);
const filterableProperties = ref({});
const pointsPromise = ref();

const currentPageText = computed(() => {
    const headerObj = {};
    if (props.defaultViewType === 'streams') {
        headerObj.title = 'Streamflow Gauges';
        headerObj.paragraph = `Points on the map represent streamflow monitoring stations.
            Control which stations are visible using the checkboxes and filter below. Click
            any marker on the map, or item in the list below, to access monitoring data.`;
    } else if (props.defaultViewType === 'wells') {
        headerObj.title = 'Observation Wells';
        headerObj.paragraph = `Points on the map represent groundwater observation wells. Control
            which wells are visible using the checkboxes and filter below. Click any marker on the map,
            or item in the list below, to access monitoring data.`;
    } else if (props.defaultViewType === 'ground') {
        headerObj.title = 'Ground Water Quality';
        headerObj.paragraph = `Points on the map represent groundwater quality monitoring stations.
            Control which stations are visible using the checkboxes and filter below. Click any marker
            on the map, or item in the list below, to access monitoring data.`;
    } else if (props.defaultViewType === 'surface') {
        headerObj.title = 'Water Quality Stations';
        headerObj.paragraph = `Points on the map represent surface water quality monitoring stations.
            Control which stations are visible using the checkboxes and filter below. Click any marker on
            the map, or item in the list below, to access monitoring data.`;
    } else if (props.defaultViewType === 'climate') {
        headerObj.title = 'Weather Stations';
        headerObj.paragraph = `Points on the map represent weather monitoring stations. Control which stations
            are visible using the checkboxes and filter below. Click any marker on the map, or item in the list
            below, to access monitoring data.`;
    }
    return headerObj;
});

const pointCount = computed(() => {
    if (points.value) return points.value.length;
    return 0;
});

onMounted(() => {
    portalHandler.viewType = props.defaultViewType;
    pointsPromise.value = new Promise(resolve => {
        resolve(fetchCache.fetchWaterPortalPoints(portalHandler.viewType));
    });
});

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

    points.value = await pointsPromise.value;
    filteredFeatures.value = points.value.features;
    sidebarFeatures.value = getVisibleLicenses(filteredFeatures.value);
    filterableProperties.value = getFilterableProperties(points.value.features);

    if (!map.value.getSource("point-source")) {
        const featureJson = {
            type: "geojson",
            data: points.value,
        };
        allFeatures.value = points.value.features;
        map.value.addSource("point-source", featureJson);
    }

    if (!map.value.getLayer("highlight-layer")) {
        map.value.addLayer(highlightLayer);
    }

    if (!map.value.getLayer("point-layer")) {
        map.value.addLayer(pointLayer);

        // check router for viewtype
        if (route.path.includes('streamflow')) {
            portalHandler.updateViewType('streams');
        }
        if (route.path.includes('groundwater/level')) {
            portalHandler.updateViewType('wells');
        }
        if (route.path.includes('surface-water')) {
            portalHandler.updateViewType('surface');
        }
        if (route.path.includes('groundwater/quality')) {
            portalHandler.updateViewType('ground');
        }
        if(route.path.includes('climate')){
            portalHandler.updateViewType('climate');
        }

        setPointPaint();
    }

    map.value.on("click", async (ev) => {
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
                // type check here because mapbox thinks arrays are strings.
                if (typeof activePoint.value.properties.yr === 'string') {
                    activePoint.value.properties.yr = JSON.parse(activePoint.value.properties.yr)
                }
            }
            if (point.length > 1) {
                featuresUnderCursor.value = point;
                showMultiPointPopup.value = true;
            }
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

const downloadCSV = async () => {
    await downloadCSVByTypeAndId(portalHandler.viewType, activePoint.value.properties.id);
}

const onViewTypeUpdate = async (newViewType) => {
    // reset selection info
    loadingMsg.value = 'Loading. Please wait...';

    // clear points data
    if (map.value.getSource("point-source")) {
        map.value.getSource('point-source').setData({
            type: "FeatureCollection",
            features: []
        });
    }

    activePoint.value = null;
    reportData.value = null;
    showReport.value = false;
    updateFilters(null);

    loading.value = true;
    points.value = await fetchCache.fetchWaterPortalPoints(newViewType);
    filteredFeatures.value = points.value.features;
    sidebarFeatures.value = getVisibleLicenses(filteredFeatures.value);
    filterableProperties.value = getFilterableProperties(points.value.features);

    try {
        if (!map.value.getSource("point-source")) {
            const featureJson = {
                type: "geojson",
                data: points.value,
            };
            map.value.addSource("point-source", featureJson);
        } else {
            map.value.getSource('point-source').setData(points.value);
        }
        allFeatures.value = points.value.features;
        pointsLoading.value = true;
        map.value.on('idle', () => {
            sidebarFeatures.value = getVisibleLicenses(filteredFeatures.value);
        });
    } catch (err) {
        console.error(err);
        Notify.create({ message: 'Unable to set the view type. Please try again later.' });
    } finally {
        loading.value = false;
    }
    setPointPaint();
}

const setPointPaint = () => {
    const propToCheck = 'status';
    const current = ["Active, Non real-time", "Active, Real-time, Responding", "Active, Real-time, Not responding"];
    const historical = "Historical";

    map.value.setPaintProperty("point-layer", "circle-color", [
        "match",
        ["get", propToCheck],
        historical,
        "#61913d",
        current,
        "#f2c037",
        "#ccc",
    ]);
}

const closeReport = () => {
    showReport.value = false;
    reportData.value = null;
}

const getReportForPoint = async () => {
    loadingMsg.value = 'Report data loading. Please wait...';
    loading.value = true;
    try {
        reportData.value = await getWaterPortalReportDataByIdAndType(activePoint.value.properties.id, portalHandler.viewType);
        showReport.value = true;
    }
    catch (err) {
        console.error(err);
        Notify.create({ message: 'Unable to fetch report data at the selected location. Please try again later.' });
    } finally {
        loading.value = false;
    }
};

/**
 * Receive a point from the map filters component and highlight it on screen
 * @param newPoint Selected Point
 */
const selectPoint = (newPoint) => {
    try {
        if (newPoint) {
            map.value.setFilter("highlight-layer", ["==", "id", newPoint.properties.id]);
            activePoint.value = newPoint;
            if (typeof activePoint.value.properties.yr === 'string') {
                activePoint.value.properties.yr = JSON.parse(activePoint.value.properties.yr)
            };

        }
        showMultiPointPopup.value = false;
    } catch(err) {
        console.error(err);
        Notify.create({ message: 'Unable to fetch point details at the selected location. Please try again later.', type: 'negative' });
    }
};

/**
 * Receive changes to filters from MapFilters component and apply filters to the map
 * @param newFilters Filters passed from MapFilters
 */
const updateFilters = (newFilters) => {
    if (!newFilters) return;
    // set the filtering
    pointsLoading.value = true;

    // set the current map features based on what is visible and filtered out
    filteredFeatures.value = getFilteredPoints(points.value.features, newFilters.matchFilters, newFilters.uniqueFilters);

    // update the map source with the new filtered points
    if (map.value.getSource('point-source')) {
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
 * Dismiss the map popup and clear the highlight layer
 */
const dismissPopup = () => {
    activePoint.value = null;
    map.value.setFilter("highlight-layer", false);
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
        const lngLat = new maplibregl.LngLat(coordinates[0], coordinates[1]);

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

const getFilterableProperties = (points) => {
    return getFilterablePropertiesByViewType(portalHandler.viewType, points);
}

</script>
