<template>
    <div>
        <h1 class="q-mb-lg">Hydrologic Variability</h1>
        <p>
            The potential variability of flows in the query basin has been estimated by comparing its physical and environmental characteristics to other watersheds which have hydrometric monitoring records. A similarity score was used to quantify the basin comparisons using multiple physical and environmental metrics. The statistical distribution of streamflows for each month from the monitored watersheds, was then used to estimate a potential range of flows for the query basin. The physical and hydroclimatic characteristics and comparisons are based on those used for hierarchical clustering of river ecosystems in BC. The location of the basins is shown on the map below.
        </p>
        <div class="annual-hydrology-map">
            <section id="hydrologicVariabilityMapContainer" class="map-container" />
        </div>
        <!-- {{ Object.keys(props.reportContent) }} -->
        <pre>{{ mapPolygons }}</pre>
        <hr>
        <pre>{{ props.reportContent.overview.mgmt_polygon }}</pre>
        <!-- {{ props.reportContent.hydrologicVariabilityDistanceValues }} -->
        <p>The watersheds shown on the map above have been identified as the most similar to the watershed described in this report. The table below shows key characteristics of these watersheds in relation to the watershed described in this report.</p>
        <hr>
    </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import foundryLogo from "@/assets/foundryLogo.svg";
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

const map = ref(null);

const mapPolygons = computed(() => {
    const myPolygons = {
        type: "FeatureCollection",
        features: [],
    };
    props.reportContent.hydrologicVariabilityMiniMapGeoJson.forEach(feature => {
        console.log(feature)

        myPolygons.features.push({
            type: "Feature",
            properties: {
                color: feature.candidate,
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
                    "line-color": "#1e1436",
                },
            });

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
