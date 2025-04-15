<template>
    <div>
        <div class="page-container">
            <Map @loaded="(map) => loadPoints(map)" />
            <div v-if="activePoint" class="point-info">
                <div class="row justify-between">
                    <h3>{{ activePoint.id }}</h3>
                    <q-icon
                        name="close"
                        size="md"
                        class="cursor-pointer"
                        @click="dismissPopup()"
                    />
                </div>
                <pre>{{ activePoint }}</pre>
                <q-btn
                    label="View Report"
                    color="primary"
                    @click="reportOpen = true"
                />
            </div>
            <MapFilters
                :points-to-show="features"
                :filters="watershedFilters"
                @update-filter="(newFilters) => updateFilters(newFilters)"
            />
        </div>
        <WatershedReport
            :report-open="reportOpen"
            @close="reportOpen = false"
        />
    </div>
</template>

<script setup>
import Map from "@/components/Map.vue";
import MapFilters from "@/components/MapFilters.vue";
import WatershedReport from "@/components/watershed/WatershedReport.vue";
import { highlightLayer, pointLayer } from "@/constants/mapLayers.js";
import points from "@/constants/watershed.json";
import { ref } from "vue";
import mapboxgl from "mapbox-gl";

const map = ref();
const activePoint = ref();
const reportOpen = ref(false);
const features = ref([]);
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
        map.value.setPaintProperty("point-layer", "circle-color", [
            "match",
            ["get", "term"],
            0,
            "#61913d",
            1,
            "#234075",
            "#ccc",
        ]);
        // Without the timeout this function gets called before the map has time to update
        setTimeout(() => {
            getVisibleLicenses();
        }, 500);
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

    map.value.on("mouseenter", "point-layer", () => {
        map.value.getCanvas().style.cursor = "pointer";
    });

    map.value.on("mouseleave", "point-layer", () => {
        map.value.getCanvas().style.cursor = "";
    });

    map.value.on("moveend", (ev) => {
        // console.log(ev);
        // console.log(map.value.getBounds());
        getVisibleLicenses();
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

    if (newFilters.buttons.find((filter) => filter.label === "Surface Water").value) {
        mapFilter.push(["==", "term", 0]);
    }
    if (newFilters.buttons.find((filter) => filter.label === "Ground Water").value) {
        mapFilter.push(["==", "term", 1]);
    }

    map.value.setFilter("point-layer", mapFilter);
    // Without the timeout this function gets called before the map has time to update
    setTimeout(() => {
        getVisibleLicenses();
    }, 500);
};

const getVisibleLicenses = () => {
    features.value = map.value.queryRenderedFeatures({
        layers: ["point-layer"],
    });
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
