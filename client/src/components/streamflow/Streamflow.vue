<template>
    <div>
        <div class="page-container">
            <Map @loaded="(map) => loadPoints(map)" />
            <div v-if="activePoint" class="point-info">
                <div class="row justify-between">
                    <h3>{{ activePoint.name }}</h3>
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
                :filters="streamflowFilters"
                :total-point-count="points.features.length"
                @update-filter="(newFilters) => updateFilters(newFilters)"
            />
        </div>
        <!-- Put Streamflow Report Here -->
        <!-- <WatershedReport
            :report-open="reportOpen"
            @close="reportOpen = false"
        /> -->
    </div>
</template>

<script setup>
import Map from "@/components/Map.vue";
import MapFilters from "@/components/MapFilters.vue";
import { highlightLayer, pointLayer } from "@/constants/mapLayers.js";
import points from "@/constants/streamflow.json";
import { ref } from "vue";

const map = ref();
const activePoint = ref();
const features = ref([]);
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
            activePoint.value = point[0].properties;
        }
    });
};

/**
 * Dismiss the map popup and clear the highlight layer
 */
const dismissPopup = () => {
    activePoint.value = null;
    map.value.setFilter("highlight-layer", false);
};

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
.map {
    height: auto;
}
</style>
