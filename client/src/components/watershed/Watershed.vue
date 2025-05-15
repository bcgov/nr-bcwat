<template>
    <div>
        <div class="page-container">
            <MapFilters
                title="Water Allocations"
                :loading="pointsLoading"
                :points-to-show="features"
                :active-point-id="activePoint?.id"
                :total-point-count="points.features.length"
                :filters="watershedFilters"
                @update-filter="(newFilters) => updateFilters(newFilters)"
                @select-point="(point) => selectPoint(point)"
                @view-more="reportOpen = true"
            />
            <div class="map-container">
                <MapSearch 
                    v-if="watershedSearchTypes.length > 0"
                    :map-points-data="features"
                    :page-search-types="watershedSearchTypes"
                    @go-to-location="onSearchSelect"
                />
                <Map @loaded="(map) => loadPoints(map)" />
            </div>
        </div>
        <WatershedReport
            v-if="clickedPoint"
            :report-open="reportOpen"
            :report-content="reportContent"
            :clicked-point="clickedPoint"
            @close="
                reportOpen = false;
                clickedPoint = null;
            "
        />
    </div>
</template>

<script setup>
import Map from "@/components/Map.vue";
import MapSearch from "@/components/MapSearch.vue";
import MapFilters from "@/components/MapFilters.vue";
import WatershedReport from "@/components/watershed/WatershedReport.vue";
import { highlightLayer, pointLayer } from "@/constants/mapLayers.js";
import points from "@/constants/watershed.json";
import reportContent from "@/constants/watershedReport.json";
import { ref } from "vue";

const map = ref();
const pointsLoading = ref(false);
const activePoint = ref();
const clickedPoint = ref();
const reportOpen = ref(false);
const features = ref([]);
const watershedSearchTypes = [
    {
        label: 'Station ID',
        type: 'stationId',
        property: 'id',
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
            return [selectedIdResult.geometry.coordinates, map.value];
        },
    }
];
const watershedFilters = ref({
    buttons: [
        {
            value: true,
            label: "Surface Water",
            color: "green-1",
        },
        {
            value: true,
            label: "Ground Water",
            color: "blue-1",
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
    pointsLoading.value = true;
    if (!map.value.getSource("point-source")) {
        const featureJson = {
            type: "geojson",
            data: points,
        };
        map.value.addSource("point-source", featureJson);
    }
    if (!map.value.getLayer("point-layer")) {
        map.value.addLayer(pointLayer);
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

        if (point.length > 0) {
            map.value.setFilter("highlight-layer", [
                "==",
                "id",
                point[0].properties.id,
            ]);
            activePoint.value = point[0].properties;
        }
    });

    map.value.on("click", (ev) => {
        clickedPoint.value = ev.lngLat;
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
};

/**
 * Receive changes to filters from MapFilters component and apply filters to the map
 * @param newFilters Filters passed from MapFilters
 */
const updateFilters = (newFilters) => {
    // Not sure if updating these here matters, the emitted filter is what gets used by the map
    watershedFilters.value = newFilters;

    const mapFilter = ["any"];

    if (
        newFilters.buttons.find((filter) => filter.label === "Surface Water")
            .value
    ) {
        mapFilter.push(["==", "term", 0]);
    }
    if (
        newFilters.buttons.find((filter) => filter.label === "Ground Water")
            .value
    ) {
        mapFilter.push(["==", "term", 1]);
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
    map.value.setFilter("highlight-layer", ["==", "id", newPoint.id]);
    activePoint.value = newPoint;
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
