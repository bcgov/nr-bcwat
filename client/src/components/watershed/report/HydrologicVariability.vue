<template>
    <div>
        <h1 class="q-my-lg">Hydrologic Variability</h1>
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
        <div class="watershed-report-map">
            <section
                id="hydrologicVariabilityMapContainer"
                class="map-container"
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

        <HydrologicVariabilityWatershedTable
            :table-data="props.reportContent.hydrologicVariabilityClimateData"
            :watershed-name="props.reportContent.overview.watershedName"
        />

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

        <h2>Tabular Data - Hydrologic Variability</h2>
        <HydrologicVariabilityTabularData
            candidate="1"
            :table-data="
                props.reportContent.hydrologicVariability['Candidate1']
            "
            color-accent="#c694c3"
            color="#8f3d96"
        />
        <HydrologicVariabilityTabularData
            :table-data="
                props.reportContent.hydrologicVariability['Candidate2']
            "
            candidate="2"
            color-accent="#7a85c1"
            color="#32429b"
        />
        <HydrologicVariabilityTabularData
            :table-data="
                props.reportContent.hydrologicVariability['Candidate3']
            "
            candidate="3"
            color-accent="#95c8ec"
            color="#418ecc"
        />
        <hr class="q-my-xl" />
    </div>
</template>

<script setup>
import HydrologicVariabilityBarChart from "@/components/watershed/report/HydrologicVariabilityBarChart.vue";
import HydrologicVariabilityTabularData from "@/components/watershed/report/HydrologicVariabilityTabularData.vue";
import HydrologicVariabilityWatershedTable from "@/components/watershed/report/HydrologicVariabilityWatershedTable.vue";
import MapMarker from "@/components/watershed/report/MapMarker.vue";
import NoteLink from "@/components/watershed/report/NoteLink.vue";
import foundryLogo from "@/assets/foundryLogo.svg";
import { computed, onMounted, ref } from "vue";
import mapboxgl from "mapbox-gl";
import { env } from '@/env'

const props = defineProps({
    reportContent: {
        type: Object,
        default: () => {},
    },
    clickedPoint: {
        type: Object,
        default: () => {},
    },
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

const map = ref(null);

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
                    color: mapLegendColors[idx],
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
    map.value = new mapboxgl.Map({
        container: "hydrologicVariabilityMapContainer",
        style: "mapbox://styles/foundryspatial/clkrhe0yc009j01pufslzevl4",
        center: {
            lat: props.reportContent.overview.mgmt_lat,
            lng: props.reportContent.overview.mgmt_lng,
        },
        zoom: 5,
        attributionControl: false,
        logoPosition: "bottom-left",
    });
    map.value.addControl(
        new mapboxgl.AttributionControl({
            customAttribution: `<a target="_blank" href="https://www.foundryspatial.com/">
                <img style="margin: -3px 0 -3px 2px; width: 15px;" src="${foundryLogo}">
            </a>`,
        })
    );
    map.value.addControl(new mapboxgl.ScaleControl(), "bottom-left");
    map.value.on("load", () => {
        // Add map layers and points
        if (!map.value.getSource("annual-hydrology-source")) {
            map.value.scrollZoom.disable();

            // Add polygon for user selected polygon
            map.value.addSource("annual-hydrology-source", {
                type: "geojson",
                data: {
                    type: "Feature",
                    geometry: props.reportContent.overview.query_polygon,
                },
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

            new mapboxgl.Marker({ color: "#cc5207" })
                .setLngLat([props.clickedPoint.lng, props.clickedPoint.lat])
                .addTo(map.value);
        }
        if (mapPolygons.value.features.length < 1) return;
        // fit to bounding box of the watershed polygon
        const bounds = new mapboxgl.LngLatBounds();
        mapPolygons.value.features.forEach((polygon) => {
            polygon.geometry.coordinates[0].forEach((coord) => {
                bounds.extend(coord);
            });
        });

        map.value.fitBounds(bounds, {
            padding: 50,
            animate: false,
        });
    });
});
</script>

<style lang="scss">
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
        height: 20px;
        width: 20px;
    }
}
</style>
