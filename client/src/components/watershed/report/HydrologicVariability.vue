<template>
    <div>
        <h1 class="q-mb-lg">Hydrologic Variability</h1>
        <p>
            The potential variability of flows in the query basin has been estimated by comparing its physical and environmental characteristics to other watersheds which have hydrometric monitoring records. A similarity score was used to quantify the basin comparisons using multiple physical and environmental metrics. The statistical distribution of streamflows for each month from the monitored watersheds, was then used to estimate a potential range of flows for the query basin. The physical and hydroclimatic characteristics and comparisons are based on those used for hierarchical clustering of river ecosystems in BC. The location of the basins is shown on the map below.
        </p>
        <div class="watershed-report-map">
            <section id="hydrologicVariabilityMapContainer" class="map-container" />
        </div>
        <div class="hydrologic-map-legend">
            <div>
                <MapMarker fill="#cc5207"/>
                Query Watershed
            </div>
            <div
                v-for="(polygon, idx) in props.reportContent.hydrologicVariabilityMiniMapGeoJson"
                :key="idx"
            >
                <span class="legend-circle" :style="{'background-color': mapLegendColors[idx % 8]}" />
                {{ polygon.candidate }}
            </div>
        </div>
        {{ Object.keys(props.reportContent).filter(key => key.includes('hydrologic')) }}
        <h2>Tabular Data - Hydrologic Variability</h2>
        <HydrologicVariabilityTabularData
            candidate="1"
            :table-data="props.reportContent.hydrologicVariability['Candidate 1']"
            color-accent="#c694c3"
            color="#8f3d96"
        />
        <HydrologicVariabilityTabularData
            :table-data="props.reportContent.hydrologicVariability['Candidate 2']"
            candidate="2"
            color-accent="#7a85c1"
            color="#32429b"
        />
        <HydrologicVariabilityTabularData
            :table-data="props.reportContent.hydrologicVariability['Candidate 3']"
            candidate="3"
            color-accent="#95c8ec"
            color="#418ecc"
        />
        <p>The watersheds shown on the map above have been identified as the most similar to the watershed described in this report. The table below shows key characteristics of these watersheds in relation to the watershed described in this report.</p>
        <hr>
    </div>
</template>

<script setup>
import HydrologicVariabilityTabularData from "@/components/watershed/report/HydrologicVariabilityTabularData.vue";
import MapMarker from "@/components/watershed/report/MapMarker.vue";
import foundryLogo from "@/assets/foundryLogo.svg";
import { computed, onMounted, ref } from "vue";
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
});

const mapLegendColors = ['#1f76b4', '#aec7e8', '#2ca02c', '#98df8a', '#d62728', '#ff9896', '#9467bd', '#c5b0d5'];

const map = ref(null);

const mapPolygons = computed(() => {
    const myPolygons = {
        type: "FeatureCollection",
        features: [],
    };
    props.reportContent.hydrologicVariabilityMiniMapGeoJson.forEach((feature, idx) => {
        myPolygons.features.push({
            type: "Feature",
            properties: {
                color: mapLegendColors[idx],
            },
            geometry: feature.geom,
        });
    })
    return myPolygons;
});

/**
 * Create MapBox map. Add universal map controls. Emit to the parent component for page specific setup
 */
 onMounted(() => {
    mapboxgl.accessToken = import.meta.env.VITE_APP_MAPBOX_TOKEN;
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
    });

    // fit to bounding box of the watershed polygon
    // const bounds = new mapboxgl.LngLatBounds();
    // props.reportContent.overview.mgmt_polygon.coordinates[0].forEach(
    //     (coord) => {
    //         bounds.extend(coord);
    //     }
    // );

    // map.value.fitBounds(bounds, {
    //     padding: 50,
    //     animate: false,
    // });
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
