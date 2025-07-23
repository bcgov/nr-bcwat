<template>
    <div 
        v-if="mapLoading"
        class="loader-container"
    >
        <q-spinner 
            class="map-loader"
            size="xl"
        />
        <div>
            Loading points. Please wait...
        </div>
    </div>
    <div>
        <div class="page-container">
            <MapFilters
                title="Water Allocations"
                :loading="pointsLoading"
                :points-to-show="features"
                :active-point-id="activePoint?.id"
                :total-point-count="pointCount"
                :filters="watershedFilters"
                :view-more="false"
                :has-flow-quantity="true"
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
                />
                <Map 
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
                                @click="openReport"
                            >
                                View Report
                            </q-btn>
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
            @close="
                reportOpen = false;
            "
        />
    </div>
</template>

<script setup>
import Map from "@/components/Map.vue";
import MapSearch from "@/components/MapSearch.vue";
import MapFilters from "@/components/MapFilters.vue";
import MapPointSelector from "@/components/MapPointSelector.vue";
import WatershedReport from "@/components/watershed/WatershedReport.vue";
import { buildFilteringExpressions } from '@/utils/mapHelpers.js';
import { getAllWatershedStations, getWatershedByLatLng, getWatershedReportByWFI } from '@/utils/api.js';
import { highlightLayer, pointLayer } from "@/constants/mapLayers.js";
import { computed, ref } from "vue";

const map = ref();
const points = ref();
const pointsLoading = ref(false);
const reportContent = ref(null);
const activePoint = ref();
const clickedPoint = ref(null);
const showMultiPointPopup = ref(false);
const watershedInfo = ref(null);
const reportOpen = ref(false);
const features = ref([]);
const mapLoading = ref(false);
const allFeatures = ref([]);
const featuresUnderCursor = ref([]);
// page-specific data search handlers
const watershedSearchableProperties = [
    { label: 'Station Name', type: 'stationName', property: 'name' },
    { label: 'Station ID', type: 'stationId', property: 'id' }
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
        network: [
            { 
                value: true,
                label: "BC Ministry of Forests", 
                key: "net",
                matches: "BC Ministry of Forests",
            },
            { 
                value: true,
                label: "ERAA", 
                key: "net",
                matches: "ERAA",
            },
            { 
                value: true,
                label: "Canada Energy Regulator", 
                key: "net",
                matches: "Canada Energy Regulator",
            },
        ]
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
    points.value = await getAllWatershedStations();
    
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
            ["get", "type"],
            "SW",
            "#61913d",
            "GW",
            "#234075",
            "#ccc",
        ]);
    }
    if (!map.value.getLayer("highlight-layer")) {
        map.value.addLayer(highlightLayer);
    }

    map.value.on("click", async (ev) => {
        watershedInfo.value = null;
        const point = map.value.queryRenderedFeatures(ev.point, {
            layers: ["point-layer"],
        });

        if(point.length){
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
                featuresUnderCursor.value = point;
                showMultiPointPopup.value = true;
            }
        } else {
            clickedPoint.value = ev.lngLat;
            // TODO: Make api call here to fetch watershed polygon for lat/lng 
            // and generate the report. 
            watershedInfo.value = await getWatershedByLatLng(ev.lngLat);
            if(watershedInfo.value && 'geojson' in watershedInfo.value){
                try {
                    if(map.value.getSource('watershed-polygon-source')){
                        map.value.getSource('watershed-polygon-source').setData(watershedInfo.value.geojson);
                    } else {
                        map.value.addSource('watershed-polygon-source', {
                            type: 'geojson',
                            data: watershedInfo.value.geojson
                        });
                    }

                    if(!map.value.getLayer('watershed-polygon-layer')){
                        map.value.addLayer({
                            'id': 'watershed-polygon-layer',
                            'source': 'watershed-polygon-source',
                            'type': 'fill',
                            'paint': {
                                'fill-color': 'orange',
                                'fill-opacity': 0.6
                            }
                        });
                    }
                } catch(e){
                    console.error('unable to set wateshed polygon');
                }
            }
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

const openReport = async () => {
    reportContent.value = await getWatershedReportByWFI(123);
    if(reportContent.value){
        reportOpen.value = true;
    }
}

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
        features.value = getVisibleLicenses();
        const selectedFeature = features.value.find(
            (feature) => feature.properties.id === activePoint.value?.id
        );
        if (selectedFeature === undefined) dismissPopup();
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
    }
    showMultiPointPopup.value = false;
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

const closeWatershedInfo = () => {
    watershedInfo.value = null;
}

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
