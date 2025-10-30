<template>
    <div>
        <div
            v-if="loading"
            class="map-loader-container"
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
                    :points-to-show="features"
                    :selected-point-from-map="activePoint"
                    :map="map"
                    :total-point-count="pointCount"
                    :filters="waterPortalFilters"
                    page="water-portal"
                    :view-more="true"
                    :has-flow-quantity="true"
                    :has-area="true"
                    :has-year-range="true"
                    :view-extent-on="map?.getZoom() < 9"
                    @update-filter="updateFilters"
                    @select-point="selectPoint"
                    @view-more="getReportForPoint"
                />
                <div class="map-container">
                    <MapSearch
                        v-if="map && allFeatures && allFeatures.length > 0 && waterPortalSearchableProperties && waterPortalSearchableProperties.length > 0"
                        :map="map"
                        :map-points-data="allFeatures"
                        :searchable-properties="waterPortalSearchableProperties"
                        @go-to-location="(coordinates) => clickMap(coordinates)"
                        @geolocate="geolocate"
                        @place-marker="createMarker"
                    />
                    <Map
                        map-type="watershed"
                        @loaded="(map) => loadPoints(map)"
                        :has-controls="true"
                    />
                    <MapPointSelector
                        :points="featuresUnderCursor"
                        :open="showMultiPointPopup"
                        @close="selectPoint"
                    />
                    <!-- <WaterPortalReport 
                        v-if="reportData && showReport"
                        :report-open="showReport"
                        :report-data="reportData"
                        :active-point="activePoint"
                        :report-type="portalHandler.viewType"
                        @close="closeReport"
                    /> -->
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
// import WaterPortalReport from '@/components/portal/WaterPortalReport.vue';
import { portalHandler } from '@/utils/reactor.js';
import { geolocate, buildFilteringExpressions } from '@/utils/mapHelpers.js';
import { highlightLayer, pointLayer } from "@/constants/mapLayers.js";
import { 
    getWaterPortalStations, 
    getWaterPortalReportDataByIdAndType 
} from '@/utils/api.js';
import { useRoute } from 'vue-router';
import { computed, ref, watch } from 'vue';
import { Notify } from 'quasar';

const route = useRoute();

// page-specific data search handlers
const waterPortalSearchableProperties = [
    { label: 'UTM', type: 'coords', property: 'nid' },
    { label: 'WFI', type: 'watershed-feature', property: 'wfi' },
];

watch(() => portalHandler.viewType, async (newViewType) => {
    await onViewTypeUpdate(newViewType);
});

const props = defineProps({
    defaultViewType: {
        type: String,
        default: 'streams',
        required: true
    }
});

const waterPortalFilters = ref({
    buttons: [],
    other: {
        network: [
            { label: 'BC Energy Regulator', key: 'net', value: true, matches: 'long' },
            { label: 'BC ENV - Real-time Water Data Reporting', key: 'net', value: true,  matches: 'short' },
            { label: 'BC Environmental Assessment Office (EAO)', key: 'net', value: true, matches: 'short' },
            { label: 'Geoscience BC', key: 'net', value: true, matches: 'Geoscience BC' },
            { label: 'Oil and Gas Industry Network', key: 'net', value: true, matches: 'Oil and Gas Industry Network' },
            { label: 'UNBC (Collected for academic research project)', key: 'net', value: true, matches: 'UNBC (Collected for academic research project)' },
            { label: 'Water Survey of Canada', key: 'net', value: true, matches: 'Water Survey of Canada' }
        ],
        status: [
            { label: "Active Appl.", key: 'status', value: true, matches: "ACTIVE APPL." },
            { label: "Current", key: 'status', value: true, matches: "CURRENT" },
        ],
        type: [
            { label: "Year Round", key: 'ty', value: true, matches: "Commercial" },
            { label: "Seasonal", key: 'ty', value: true, matches: "Agriculture" },
        ],
    },
});
const map = ref(null);
const points = ref([]);
const pointsLoading = ref(false);
const activePoint = ref(null);
const loading = ref(false);
const loadingMsg = ref('Loading. Please wait...');
const features = ref([]);
const allFeatures = ref([]);
const featuresUnderCursor = ref([]);
const showMultiPointPopup = ref(false);
const showReport = ref(false);
const firstSymbolId = ref();
const allQueriedPoints = ref([]);
const marker = ref(null);
const reportData = ref(null);

const currentPageText = computed(() => {
    const headerObj = {};
    if(props.defaultViewType === 'streams'){
        headerObj.title = 'Streamflow Gauges';
        headerObj.paragraph = `Points on the map represent streamflow monitoring stations. 
            Control which stations are visible using the checkboxes and filter below. Click 
            any marker on the map, or item in the list below, to access monitoring data.`;
    } else if(props.defaultViewType === 'wells'){
        headerObj.title = 'Observation Wells';
        headerObj.paragraph = `Points on the map represent groundwater observation wells. Control 
            which wells are visible using the checkboxes and filter below. Click any marker on the map, 
            or item in the list below, to access monitoring data.`;
    } else if(props.defaultViewType === 'ground'){
        headerObj.title = 'Ground Water Quality';
        headerObj.paragraph = `Points on the map represent groundwater quality monitoring stations. 
            Control which stations are visible using the checkboxes and filter below. Click any marker 
            on the map, or item in the list below, to access monitoring data.`;
    } else if(props.defaultViewType === 'surface'){
        headerObj.title = 'Water Quality Stations';
        headerObj.paragraph = `Points on the map represent surface water quality monitoring stations. 
            Control which stations are visible using the checkboxes and filter below. Click any marker on 
            the map, or item in the list below, to access monitoring data.`;
    } else if(props.defaultViewType === 'weather'){
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

    points.value = await getWaterPortalStations(props.defaultViewType);

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

        // check router for viewtype
        if(route.path.includes('streamflow')){
            portalHandler.updateViewType('streams');
        }
        if(route.path.includes('groundwater/level')){
            portalHandler.updateViewType('wells');
        }
        if(route.path.includes('surface-water')){
            portalHandler.updateViewType('surface');
        }
        if(route.path.includes('groundwater/quality')){
            portalHandler.updateViewType('ground');
        }
        if(route.path.includes('climate')){
            portalHandler.updateViewType('weather');
        }
        
        setPointPaint();
    }
    if (!map.value.getLayer("highlight-layer")) {
        map.value.addLayer(highlightLayer);
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

    map.value.on('movestart', () => {
        pointsLoading.value = true;
    })

    map.value.on("moveend", () => {
        features.value = getVisibleLicenses();
        pointsLoading.value = false;
    });

    map.value.once("idle", () => {
        features.value = getVisibleLicenses();
        pointsLoading.value = false;
    });
    
    loading.value = false;
};

const onViewTypeUpdate = async (newViewType) => {
    // reset selection info
    loadingMsg.value = 'Loading. Please wait...';
    activePoint.value = null;
    reportData.value = null;
    showReport.value = false;
    map.value.setFilter("highlight-layer", ["==", "id", "nevergonnagiveyouup"]);

    loading.value = true;
    points.value = await getWaterPortalStations(newViewType);
    try{
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
            features.value = getVisibleLicenses();
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
    try{
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
 * Receive a point from the map filters component and highlight it on screen
 * @param newPoint Selected Point
 */
const selectPoint = (newPoint) => {
    try {
        if (newPoint) {
            map.value.setFilter("highlight-layer", ["==", "id", newPoint.properties.id]);
            activePoint.value = newPoint;
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
    // Not sure if updating these here matters, the emitted filter is what gets used by the map
    waterPortalFilters.value = newFilters;
    const mapFilter = buildFilteringExpressions(newFilters, true);
    map.value.setFilter("point-layer", mapFilter);

    setTimeout(() => {
        features.value = getVisibleLicenses(true);
        const selectedFeature = features.value.find((feature) => feature.properties.id === activePoint.value?.properties.id);
        if (selectedFeature === undefined) dismissPopup();
    }, 500);
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
const getVisibleLicenses = () => {
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
</script>
