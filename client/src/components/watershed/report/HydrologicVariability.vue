<template>
    <div>
        <div>
            <div :class="props.isReport ? 'report-section-header' : ''">
                <div class="text-h4 q-my-lg">Hydrologic Variability</div>
            </div>
            <p>
                The potential variability of flows in the query basin has been
                estimated by comparing its physical and environmental
                characteristics to other watersheds which have hydrometric
                monitoring records. A similarity score was used to quantify the
                basin comparisons using multiple physical and environmental
                metrics<NoteLink :note-number="13" />. The statistical distribution
                of streamflows for each month from the monitored watersheds, was
                then used to estimate a potential range of flows for the query
                basin. The physical and hydroclimatic characteristics and
                comparisons are based on those used for hierarchical clustering of
                river ecosystems in BC<NoteLink :note-number="14" />. The location
                of the basins is shown on the map below.
            </p>

            <div class="hydrologic-variability-map">
                <div
                    class="watershed-report-map"
                    :class="props.isReport ? 'report' : ''"
                >
                    <div
                        id="hydrologicVariabilityMapContainer"
                        class="report-map-container"
                        ref="hydrologic-variability-map-container"
                    />
                </div>
                <img
                    class="watershed-report-map-image"
                    :class="props.isReport ? 'report' : ''"
                    :src="mapSrc"
                />
            </div>
            <div class="hydrologic-map-legend">
                <div>
                    <MapMarker fill="#cc5207" />
                    Query Watershed
                </div>
                <div
                    v-for="(polygon, idx) in props.reportContent.hydrologicVariabilityMiniMapGeoJson"
                    :key="idx"
                >
                    <span
                        class="legend-circle"
                        :style="{ 'background-color': mapLegendColors[idx % 8] }"
                    />
                    {{ polygon.candidate }}
                </div>
            </div>
            <p class="q-pb-md">
                The watersheds shown on the map above have been identified as the
                most similar to the watershed described in this report. The table
                below shows key characteristics of these watersheds in relation to
                the watershed described in this report.
            </p>
        </div>

        <div>
            <HydrologicVariabilityWatershedTable
                :table-data="props.reportContent.hydrologicVariabilityClimateData"
                :watershed-name="props.reportContent.overview.watershedName"
            />
        </div>
        <div>
            <p class="q-pt-xl">
                The statistical distribution of flows, from the top 3 candidate
                basins, has been applied to the estimated mean monthly flows of the
                watershed described in this report<NoteLink :note-number="15" />.
                The chart and table below show the potential variability of flows
                using the flow duration curve replacement approach. Please refer to
                the Tabular Data - Hydrologic Variability section to determine the
                candidate gauges used for each month.
            </p>
            <HydrologicVariabilityBarChart
                :chart-data="props.reportContent.hydrologicVariability"
                :mad="props.reportContent.queryMonthlyHydrology.meanAnnualDischarge"
                :mean="props.reportContent.queryMonthlyHydrology.monthlyDischarge"
            />
        </div>

        <div class="report-break">
            <div class="text-h5 q-my-lg">Tabular Data - Hydrologic Variability</div>
            <HydrologicVariabilityTabularData
                v-for="(candidate, key, idx) in props.reportContent.hydrologicVariability"
                :key="key"
                :candidate="idx + 1"
                :table-data="candidate"
                :is-report="props.isReport"
                :color-accent="candidateAccentColors[idx]"
                :color="candidateColors[idx]"
            />

            <q-separator
                v-if="props.isReport"
                class="q-my-md"
            />

            <div
                v-if="props.isReport"
                class="report-table-legend"
            >
                <div class="candidate-legend-label">
                    Candidate 1
                    <div
                        class="legend-square"
                        :style="{ 'background-color': '#c694c3' }"
                    />
                </div>
                <div class="candidate-legend-label">
                    Candidate 2
                    <div
                        class="legend-square"
                        :style="{ 'background-color': '#7a85c1' }"
                    />
                </div>
                <div class="candidate-legend-label">
                    Candidate 3
                    <div
                        class="legend-square"
                        :style="{ 'background-color': '#95c8ec' }"
                    />
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import html2canvas from "html2canvas";
import HydrologicVariabilityBarChart from "@/components/watershed/report/HydrologicVariabilityBarChart.vue";
import HydrologicVariabilityTabularData from "@/components/watershed/report/HydrologicVariabilityTabularData.vue";
import HydrologicVariabilityWatershedTable from "@/components/watershed/report/HydrologicVariabilityWatershedTable.vue";
import MapMarker from "@/components/watershed/report/MapMarker.vue";
import NoteLink from "@/components/watershed/report/NoteLink.vue";
import { computed, onMounted, ref, useTemplateRef } from "vue";
import { customAttribution, getBoundingBox } from "@/utils/mapHelpers.js";
import maplibregl from "maplibre-gl";
import { env } from "@/env.js";
import mapboxgl from "mapbox-gl";

const props = defineProps({
    reportContent: {
        type: Object,
        default: () => {},
    },
    clickedPoint: {
        type: Object,
        default: () => {},
    },
    isReport: {
        type: Boolean,
        default: false,
    },
    points: {
        type: Object,
        default: () => {},
    }
});

const mapLegendColors = [
    "#1f76b4",
    "#aec7e8",
    "#2ca02c",
    "#98df8a",
    "#d62728",
    "#ff9896",
    "#9467bd",
    "#c5b0d5",
];
const candidateAccentColors = [
    "#c694c3",
    "#7a85c1",
    "#95c8ec",
];
const candidateColors = [
    "#8f3d96",
    "#32429b",
    "#418ecc",
];

const map = ref(null);
const mapSrc = ref("");
const mapContainer = useTemplateRef("hydrologic-variability-map-container");

const mapCenter = computed(() => {
    return props.isReport ?
        [props.reportContent.lngLat.lng, props.reportContent.lngLat.lat] :
        [props.clickedPoint.lng, props.clickedPoint.lat];
})

const mapPolygons = computed(() => {
    const myPolygons = {
        type: "FeatureCollection",
        features: [],
    };
    if (props.reportContent.hydrologicVariabilityMiniMapGeoJson) {
        props.reportContent.hydrologicVariabilityMiniMapGeoJson.forEach((feature, idx) => {
            myPolygons.features.push({
                type: "Feature",
                properties: {
                    color: mapLegendColors[idx % mapLegendColors.length],
                },
                geometry: feature.geom,
            });
        });
    }
    return myPolygons;
});

/**
 * Create MapBox map. Add universal map controls. Emit to the parent component for page specific setup
 */
onMounted(() => {
    mapboxgl.accessToken = env.VITE_APP_MAPBOX_TOKEN;
    map.value = new maplibregl.Map({
        container: "hydrologicVariabilityMapContainer",
        style: 'mapbox://styles/bcwatertool/cmds0uj4o007101re4ywuha95',
        center: {
            lat: mapCenter.value[1],
            lng: mapCenter.value[0],
        },
        zoom: 5,
        attributionControl: false,
        logoPosition: "bottom-left",
        preserveDrawingBuffer: true,
    });
    map.value.addControl(new maplibregl.AttributionControl({ customAttribution }));
    map.value.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'bottom-right');
    map.value.addControl(new maplibregl.ScaleControl(), "bottom-left");
    map.value.on("load", async () => {
        if (!map.value.getSource("point-source")) {
            const featureJson = {
                type: "geojson",
                data: props.points,
            };
            map.value.addSource("point-source", featureJson);
        }

        if (!map.value.getLayer("point-layer")) {
            map.value.addLayer({
                id: "point-layer",
                type: "circle",
                source: "point-source",
                paint: {
                    "circle-color": "#0000CD",
                    "circle-radius": {
                        base: 3,
                        stops: [
                            [6, 2],
                            [8, 4],
                            [10, 8],
                        ],
                    },
                },
            });
            map.value.setPaintProperty("point-layer", "circle-color", [
                "match",
                ["get", "type"],
                "SW",
                "#61913d",
                "GW",
                "#283593",
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

        // Add map layers and points
        if (!map.value.getSource("annual-hydrology-source")) {
            map.value.scrollZoom.disable();
            map.value.addSource("annual-hydrology-source", {
                type: "geojson",
                data: props.reportContent.overview.query_polygon,
            });
            map.value.addLayer({
                id: "watershed-polygon-layer",
                type: "fill",
                source: "annual-hydrology-source",
                paint: {
                    "fill-color": "#f26721",
                    "fill-opacity": 0.5,
                },
            });
            map.value.addLayer({
                id: "watershed-line-layer",
                type: "line",
                source: "annual-hydrology-source",
                paint: {
                    "line-color": "#f26721",
                },
            });

            // Add layer for similar watershed outlines
            map.value.addSource("downstream-source", {
                type: "geojson",
                data: mapPolygons.value,
            });
            map.value.addLayer({
                id: "downstream-line-layer",
                type: "line",
                source: "downstream-source",
                paint: {
                    "line-color": ["get", "color"],
                    "line-width": 2,
                },
            });

            // add marker as a layer
            new maplibregl.Marker({ color: "#cc5207" })
                .setLngLat(mapCenter.value)
                .addTo(map.value);
        }
        if (mapPolygons.value.features.length < 1) return;
        // fit to bounding box of the watershed polygon
        const pointFeature = {
            geometry: {
                coordinates: [props.clickedPoint.lng, props.clickedPoint.lat],
                type: "Point",
            },
            type: "Feature",
        };
        const bounds = getBoundingBox([...mapPolygons.value.features, pointFeature]);
        map.value.fitBounds(bounds, {
            padding: 100,
            animate: false,
        });
    });

    map.value.on('idle', async () => {
        // reserve the map image for the report version of the page to prevent additional load time
        if(props.isReport){
            const mapEl = await html2canvas(mapContainer.value, { logging: false });
            mapSrc.value = mapEl.toDataURL();
        }
        document.hydrologicVariabilityLoaded = true;
    });

});
</script>

<style lang="scss">
.hydrologic-variability-map {
    position: relative;
    height: 23rem;

    .watershed-report-map-image {
        position: absolute;
        top: 0;
        left: 0;
        display: none;
        width: 100%;
        z-index: 2;

        &.report {
            display: grid;
        }
    }
    .watershed-report-map {
        display: grid;
        z-index: 1;
        min-height: 23rem;

        &.report {
            height: 0;
        }
    }
}

.report-break {
    page-break-before: always;
}

.watershed-report-hydrologic-variability-map {
    position: relative;
    flex: 1;
    height: 20rem;
    margin-top: 2rem;
    margin-left: auto;
    margin-right: auto;

    .map-container {
        position: absolute;
        top: 0;
        height: 20rem;
        width: 100%;
    }
}

.hydrologic-variability-map-image {
    display: none;
    width: 100%;
}

.hydrologic-map-legend {
    align-items: center;
    background-color: $light-grey-accent;
    border: 1px solid grey;
    display: flex;
    flex-wrap: wrap;
    padding: 1em;

    svg {
        max-height: 30px;
        margin-right: 1em;
    }

    div {
        align-items: center;
        display: flex;
        flex-direction: row;
    }

    .legend-circle {
        border-radius: 50%;
        margin-left: 1em;
        margin-right: 0.5em;
        height: 12px;
        width: 12px;
    }
}

.report-table-legend {
    display: flex;
    justify-content: space-evenly;
    width: 100%;

    .candidate-legend-label {
        align-items: center;
        display: flex;
        flex-direction: row;
    }

    .legend-square {
        border-radius: 2px;
        border: 1px solid black;
        margin-left: 1em;
        margin-right: 0.5em;
        height: 15px;
        width: 15px;
    }
}
</style>
