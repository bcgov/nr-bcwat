<template>
    <div>
        <div class="page-container">
            <MapFilters
                title="Water Allocations"
                :loading="pointsLoading"
                :points-to-show="features"
                :active-point-id="activePoint?.id"
                :total-point-count="points.features.length"
                :filters="streamflowFilters"
                @update-filter="(newFilters) => updateFilters(newFilters)"
                @select-point="(point) => selectPoint(point)"
                @view-more="reportOpen = true"
            />
            <div class="map-container">
                <MapSearch 
                    v-if="streamflowSpecificSearchOptions.length > 0"
                    :map-points-data="features"
                    :page-search-options="streamflowSpecificSearchOptions"
                    :page-search-types="streamSearchTypes"
                    @go-to-location="onSearchSelect"
                />
                <Map @loaded="(map) => loadPoints(map)" />
            </div>
        </div>
        <StreamflowReport
            :active-point="activePoint"
            :report-open="reportOpen"
            @close="reportOpen = false"
        />
    </div>
</template>

<script setup>
import Map from "@/components/Map.vue";
import MapFilters from "@/components/MapFilters.vue";
import MapSearch from '@/components/MapSearch.vue';
import { highlightLayer, pointLayer } from "@/constants/mapLayers.js";
import points from "@/constants/streamflow.json";
import { nextTick, ref } from "vue";
import StreamflowReport from "./StreamflowReport.vue";

const map = ref();
const activePoint = ref();
const features = ref([]);
const pointsLoading = ref(false);
const reportOpen = ref(false);
const streamflowSpecificSearchOptions = [
    { label: 'Station Name', value: 'stationName' },
    { label: 'Station ID', value: 'stationId' },
];
const streamSearchTypes = [
    {
        type: 'stationName',
        searchFn: (stationName) => {
            const matches = features.value.filter(el => {
                return el.properties.name.substring(0, stationName.length) === stationName;
            })
            return matches;
        },
        selectFn: (selectedNameResult) => {
            // return the coordinates of the selected point and go to its location
            map.value.setFilter("highlight-layer", [
                "==",
                "id",
                selectedNameResult.properties.id,
            ]);
            activePoint.value = selectedNameResult.properties;
            onSearchSelect(selectedNameResult.geometry.coordinates);
        },
    },
    {
        type: 'stationId',
        searchFn: (stationId) => {
            const matches = features.value.filter(el => {
                return el.properties.id.toString().substring(0, stationId.length) === stationId;
            })
            return matches;
        },
        selectFn: (selectedIdResult) => {
            // return the coordinates of the selected point and go to its location
            map.value.setFilter("highlight-layer", [
                "==",
                "id",
                selectedIdResult.properties.id,
            ]);
            activePoint.value = selectedIdResult.properties;
            onSearchSelect(selectedIdResult.geometry.coordinates);
        },
    }
];
const streamflowFilters = ref({
    buttons: [
        {
            value: true,
            label: "Surface Water",
        },
        {
            value: true,
            label: "Ground Water",
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

const onSearchSelect = (coordinates) => {
    console.log(coordinates)

    map.value.flyTo({
        center: [coordinates[0], coordinates[1]],
        zoom: 10
    })
}

/**
 * Add Watershed License points to the supplied map
 * @param mapObj Mapbox Map
 */
const loadPoints = (mapObj) => {
    map.value = mapObj;
    if (!map.value.getSource("point-source")) {
        const featureJson = {
            type: "geojson",
            data: points,
        };
        map.value.addSource("point-source", featureJson);
    }
    if (!map.value.getLayer("point-layer")) {
        map.value.addLayer(pointLayer);
    }
    if (!map.value.getLayer("highlight-layer")) {
        map.value.addLayer(highlightLayer);
    }

    map.value.on("click", "point-layer", (ev) => {
        const point = map.value.queryRenderedFeatures(ev.point, {
            layers: ["point-layer"],
        });

        if (point.length > 0) {
            map.value.setFilter("highlight-layer", [
                "==",
                "id",
                point[0].properties.id,
            ]);
            point[0].properties.id = point[0].properties.id.toString();
            activePoint.value = point[0].properties;
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
};

/**
 * Receive a point from the map filters component and highlight it on screen
 * @param newPoint Selected Point
 */
 const selectPoint = (newPoint) => {
    map.value.setFilter("highlight-layer", [
        "==",
        "id",
        newPoint.id.toString(),
    ]);
    activePoint.value = newPoint;
    // force id as string to satisfy shared map filter component
    activePoint.value.id = activePoint.value.id.toString();
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
    watershedFilters.value = newFilters;

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
