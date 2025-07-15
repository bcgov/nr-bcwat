<template>
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
                    :loading="mapLoading"
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
        purpose: [
            {
                label: "Comm. Enterprise",
                matches: "Comm. Enterprise",
                key: 'org',
                value: true
            },
            {
                label: "Misc Ind'l",
                matches: "Misc Ind'l",
                key: 'org',
                value: true
            },
            {
                label: "Irrigation: Private",
                matches: "Irrigation: Private",
                key: 'org',
                value: true
            },
            {
                label: "Land Improvement: General",
                matches: "Land Improvement: General",
                key: 'org',
                value: true
            },
            {
                label: "Lwn, Fairway & Grdn",
                matches: "Lwn, Fairway & Grdn",
                key: 'org',
                value: true
            },
            {
                label: "Aquifer Storage: Non-Power",
                matches: "Aquifer Storage: Non-Power",
                key: 'org',
                value: true
            },
            {
                label: "Pond & Aquaculture",
                matches: "Pond & Aquaculture",
                key: 'org',
                value: true
            },
            {
                label: "Domestic",
                matches: "Domestic",
                key: 'org',
                value: true
            },
            {
                label: "Livestock & Animal",
                matches: "Livestock & Animal",
                key: 'org',
                value: true
            },
            {
                label: "Stream Storage: Non-Power",
                matches: "Stream Storage: Non-Power",
                key: 'org',
                value: true
            },
            {
                label: "Well Drilling/Transport Management",
                matches: "Well Drilling/Transport Management",
                key: 'org',
                value: true
            },
            {
                label: "Mining: Processing Ore",
                matches: "Mining: Processing Ore",
                key: 'org',
                value: true
            },
            {
                label: "Stream Storage: Power",
                matches: "Stream Storage: Power",
                key: 'org',
                value: true
            },
            {
                label: "Camps & Pub Facil",
                matches: "Camps & Pub Facil",
                key: 'org',
                value: true
            },
            {
                label: "Fish Hatchery",
                matches: "Fish Hatchery",
                key: 'org',
                value: true
            },
            {
                label: "Waterworks: Local Provider",
                matches: "Waterworks: Local Provider",
                key: 'org',
                value: true
            },
            {
                label: "Vehicle & Eqpt",
                matches: "Vehicle & Eqpt",
                key: 'org',
                value: true
            },
            {
                label: "Lwn, Fairway & Grdn: Watering",
                matches: "Lwn, Fairway & Grdn: Watering",
                key: 'org',
                value: true
            },
            {
                label: "Transport Mgmt: Dust Control",
                matches: "Transport Mgmt: Dust Control",
                key: 'org',
                value: true
            },
            {
                label: "Permit to Occupy Crown Land",
                matches: "Permit to Occupy Crown Land",
                key: 'org',
                value: true
            },
            {
                label: "Conservation: Storage",
                matches: "Conservation: Storage",
                key: 'org',
                value: true
            },
            {
                label: "Processing & Mfg: Fire Prevention",
                matches: "Processing & Mfg: Fire Prevention",
                key: 'org',
                value: true
            },
            {
                label: "Swimming Pool",
                matches: "Swimming Pool",
                key: 'org',
                value: true
            },
            {
                label: "Waterworks: Water Delivery",
                matches: "Waterworks: Water Delivery",
                key: 'org',
                value: true
            },
            {
                label: "Power: General",
                matches: "Power: General",
                key: 'org',
                value: true
            },
            {
                label: "Comm. Enterprise: Enterprise",
                matches: "Comm. Enterprise: Enterprise",
                key: 'org',
                value: true
            },
            {
                label: "Oil & Gas: Hydraulic Fracturing (non-deep GW)",
                matches: "Oil & Gas: Hydraulic Fracturing (non-deep GW)",
                key: 'org',
                value: true
            },
            {
                label: "Waterworks: Water Sales",
                matches: "Waterworks: Water Sales",
                key: 'org',
                value: true
            },
            {
                label: "Conservation: Use of Water",
                matches: "Conservation: Use of Water",
                key: 'org',
                value: true
            },
            {
                label: "Conservation: Construction Works",
                matches: "Conservation: Construction Works",
                key: 'org',
                value: true
            },
            {
                label: "Livestock & Animal: Stockwatering",
                matches: "Livestock & Animal: Stockwatering",
                key: 'org',
                value: true
            },
            {
                label: "Crop Harvest, Protect & Compost",
                matches: "Crop Harvest, Protect & Compost",
                key: 'org',
                value: true
            },
            {
                label: "Fresh Water Bottling",
                matches: "Fresh Water Bottling",
                key: 'org',
                value: true
            },
            {
                label: "Mining: Washing Coal",
                matches: "Mining: Washing Coal",
                key: 'org',
                value: true
            },
            {
                label: "Power: Residential",
                matches: "Power: Residential",
                key: 'org',
                value: true
            },
            {
                label: "Greenhouse & Nursery",
                matches: "Greenhouse & Nursery",
                key: 'org',
                value: true
            },
            {
                label: "Mining: Placer",
                matches: "Mining: Placer",
                key: 'org',
                value: true
            },
            {
                label: "Processing & Mfg",
                matches: "Processing & Mfg",
                key: 'org',
                value: true
            },
            {
                label: "Misc Ind'l: Sediment Control",
                matches: "Misc Ind'l: Sediment Control",
                key: 'org',
                value: true
            },
            {
                label: "Cooling",
                matches: "Cooling",
                key: 'org',
                value: true
            },
            {
                label: "Waterworks (other than LP)",
                matches: "Waterworks (other than LP)",
                key: 'org',
                value: true
            },
            {
                label: "Mineralized Water: Bottling & Dist",
                matches: "Mineralized Water: Bottling & Dist",
                key: 'org',
                value: true
            },
            {
                label: "Lwn, Fairway & Grdn: Res L/G",
                matches: "Lwn, Fairway & Grdn: Res L/G",
                key: 'org',
                value: true
            },
            {
                label: "Power: Commercial",
                matches: "Power: Commercial",
                key: 'org',
                value: true
            },
            {
                label: "Mineralized Water: Comm. Bathing Pool",
                matches: "Mineralized Water: Comm. Bathing Pool",
                key: 'org',
                value: true
            },
            {
                label: "Irrigation: Local Provider",
                matches: "Irrigation: Local Provider",
                key: 'org',
                value: true
            },
            {
                label: "Heat Exchanger, Ind'l & Comm.",
                matches: "Heat Exchanger, Ind'l & Comm.",
                key: 'org',
                value: true
            },
            {
                label: "Heat Exchanger, Residential",
                matches: "Heat Exchanger, Residential",
                key: 'org',
                value: true
            },
            {
                label: "Industrial Waste Mgmt",
                matches: "Industrial Waste Mgmt",
                key: 'org',
                value: true
            },
            {
                label: "Ind'l Waste Mgmt: Effluent",
                matches: "Ind'l Waste Mgmt: Effluent",
                key: 'org',
                value: true
            },
            {
                label: "Misc Ind'l: Fire Protection",
                matches: "Misc Ind'l: Fire Protection",
                key: 'org',
                value: true
            },
            {
                label: "Ice & Snow Making",
                matches: "Ice & Snow Making",
                key: 'org',
                value: true
            },
            {
                label: "Incidental - Domestic",
                matches: "Incidental - Domestic",
                key: 'org',
                value: true
            },
            {
                label: "Processing & Mfg: Processing",
                matches: "Processing & Mfg: Processing",
                key: 'org',
                value: true
            },
            {
                label: "Camps & Pub Facil: Public Facility",
                matches: "Camps & Pub Facil: Public Facility",
                key: 'org',
                value: true
            },
            {
                label: "Oil & Gas: Drilling",
                matches: "Oil & Gas: Drilling",
                key: 'org',
                value: true
            },
            {
                label: "Pulp Mill",
                matches: "Pulp Mill",
                key: 'org',
                value: true
            },
            {
                label: "Vehicle & Eqpt: Truck & Eqpt Wash",
                matches: "Vehicle & Eqpt: Truck & Eqpt Wash",
                key: 'org',
                value: true
            },
            {
                label: "Crops: Frost Protection",
                matches: "Crops: Frost Protection",
                key: 'org',
                value: true
            },
            {
                label: "Camps & Pub Facil: Church/Com Hall",
                matches: "Camps & Pub Facil: Church/Com Hall",
                key: 'org',
                value: true
            },
            {
                label: "Misc Ind'l: Dewatering",
                matches: "Misc Ind'l: Dewatering",
                key: 'org',
                value: true
            },
            {
                label: "Camps & Pub Facil: Institutions",
                matches: "Camps & Pub Facil: Institutions",
                key: 'org',
                value: true
            },
            {
                label: "Camps & Pub Facil: Work Camps",
                matches: "Camps & Pub Facil: Work Camps",
                key: 'org',
                value: true
            },
            {
                label: "Oil & Gas: Oil field inject. (non-deep GW)",
                matches: "Oil & Gas: Oil field inject. (non-deep GW)",
                key: 'org',
                value: true
            },
            {
                label: "Transport Mgmt: Road Maint",
                matches: "Transport Mgmt: Road Maint",
                key: 'org',
                value: true
            },
            {
                label: "Land Improvement: Ind'l for Rehab or Remed",
                matches: "Land Improvement: Ind'l for Rehab or Remed",
                key: 'org',
                value: true
            },
            {
                label: "Camps & Pub Facil: Non-Work Camps",
                matches: "Camps & Pub Facil: Non-Work Camps",
                key: 'org',
                value: true
            },
            {
                label: "Greenhouse & Nursery: Greenhouse",
                matches: "Greenhouse & Nursery: Greenhouse",
                key: 'org',
                value: true
            },
            {
                label: "Vehicle & Eqpt: Brake Cooling",
                matches: "Vehicle & Eqpt: Brake Cooling",
                key: 'org',
                value: true
            },
            {
                label: "Misc Ind'l: Overburden Disposal",
                matches: "Misc Ind'l: Overburden Disposal",
                key: 'org',
                value: true
            },
            {
                label: "Crops: Flood Harvesting",
                matches: "Crops: Flood Harvesting",
                key: 'org',
                value: true
            },
            {
                label: "Greenhouse & Nursery: Nursery",
                matches: "Greenhouse & Nursery: Nursery",
                key: 'org',
                value: true
            },
            {
                label: "Oil & Gas: Hydraulic Fracturing (deep GW)",
                matches: "Oil & Gas: Hydraulic Fracturing (deep GW)",
                key: 'org',
                value: true
            },
            {
                label: "Ice & Snow Making: Snow",
                matches: "Ice & Snow Making: Snow",
                key: 'org',
                value: true
            },
            {
                label: "Crops: Crop Suppression",
                matches: "Crops: Crop Suppression",
                key: 'org',
                value: true
            },
            {
                label: "Mining: Hydraulic",
                matches: "Mining: Hydraulic",
                key: 'org',
                value: true
            },
            {
                label: "Ind'l Waste Mgmt: Sewage Disposal",
                matches: "Ind'l Waste Mgmt: Sewage Disposal",
                key: 'org',
                value: true
            },
            {
                label: "Ice & Snow Making: Ice",
                matches: "Ice & Snow Making: Ice",
                key: 'org',
                value: true
            },
            {
                label: "Vehicle & Eqpt: Mine & Quarry",
                matches: "Vehicle & Eqpt: Mine & Quarry",
                key: 'org',
                value: true
            },
            {
                label: "Livestock & Animal: Game Farm",
                matches: "Livestock & Animal: Game Farm",
                key: 'org',
                value: true
            },
            {
                label: "River Improvement",
                matches: "River Improvement",
                key: 'org',
                value: true
            },
            {
                label: "Camps & Pub Facil: Exhibition Grounds",
                matches: "Camps & Pub Facil: Exhibition Grounds",
                key: 'org',
                value: true
            },
            {
                label: "Comm. Enterprise: Amusement Park",
                matches: "Comm. Enterprise: Amusement Park",
                key: 'org',
                value: true
            },
            {
                label: "Ind'l Waste Mgmt: Garbage Dump",
                matches: "Ind'l Waste Mgmt: Garbage Dump",
                key: 'org',
                value: true
            },
            {
                label: "Livestock & Animal: Kennel",
                matches: "Livestock & Animal: Kennel",
                key: 'org',
                value: true
            },
            {
                label: "Processing & Mfg: Wharves",
                matches: "Processing & Mfg: Wharves",
                key: 'org',
                value: true
            },
            {
                label: "Bulk Shipment for Marine Transfer ",
                matches: "Bulk Shipment for Marine Transfer ",
                key: 'org',
                value: true
            },
            {
                label: "Oil & Gas Purpose: Other",
                matches: "Oil & Gas Purpose: Other",
                key: 'org',
                value: true
            },
            {
                label: "Industrial: Pressure Testing",
                matches: "Industrial: Pressure Testing",
                key: 'org',
                value: true
            },
            {
                label: "N/A",
                matches: "N/A",
                key: 'org',
                value: true
            },
        ],
        network: [
            { 
                value: true,
                label: "BC Ministry of Forests", 
                key: 'net',
                matches: "BC Ministry of Forests",
            },
            { 
                value: true,
                label: "ERAA", 
                key: 'net',
                matches: "ERAA",
            },
            { 
                value: true,
                label: "Canada Energy Regulator", 
                key: 'net',
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

    const mainFilterExpressions = [];
    // filter expression builder for the main buttons:
    newFilters.buttons.forEach(el => {
        if(el.value){
            el.matches.forEach(match => {
                mainFilterExpressions.push(["==", ['get', el.key], match]);
            })
        }
    });

    const mainFilterExpression = ['any', ...mainFilterExpressions];

    const filterExpressions = [];
    for(const el in newFilters.other){
        const expression = [];
        newFilters.other[el].forEach(type => {
            if(type.value){
                expression.push(["==", ['get', type.key], type.matches]);
            }
        });
        filterExpressions.push(['any', ...expression])
    };

    const otherFilterExpressions = ['all', ...filterExpressions];

    // watershed-specific checks on water quantity
    const quantityRangeExpressions = ['any'];
    if('quantity' in newFilters){
        for(const el in newFilters.quantity){
            if(newFilters.quantity[el].value){
                if(newFilters.quantity[el].label.includes('or less')){
                    quantityRangeExpressions.push(["<=", ['get', newFilters.quantity[el].key], 10000]);
                }
                if(newFilters.quantity[el].label.includes('or more')){
                    quantityRangeExpressions.push([">=", ['get', newFilters.quantity[el].key], 1000000]);
                } else {
                    quantityRangeExpressions.push(['all', 
                        ['>=', ['get', newFilters.quantity[el].key], newFilters.quantity[el].low], 
                        ['<=', ['get', newFilters.quantity[el].key], newFilters.quantity[el].high]
                    ])
                }
            }
        };
    }

    const allExpressions = ["all", mainFilterExpression, otherFilterExpressions];
    if(quantityRangeExpressions.length){
        allExpressions.push(quantityRangeExpressions);
    }

    // gets the unique keys for the analysesObj for points
    // const uniqueFeats = [];
    // allFeatures.value.forEach(feature => {
    //     if(!uniqueFeats.includes(feature.properties.type)){
    //         uniqueFeats.push(feature.properties.type)
    //     }
    // });
    // console.log(uniqueFeats);

    const mapFilter = allExpressions;
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
