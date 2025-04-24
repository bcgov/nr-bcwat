<template>
    <section id="mapContainer" class="map-container" />
</template>

<script setup>
import { onMounted, ref } from "vue";
import foundryLogo from "@/assets/foundryLogo.svg";
import mapboxgl from "mapbox-gl";

const emit = defineEmits(["loaded"]);

const map = ref(null);

/**
 * Create MapBox map. Add universal map controls. Emit to the parent component for page specific setup
 */
onMounted(() => {
    mapboxgl.accessToken = import.meta.env.VITE_APP_MAPBOX_TOKEN;
    map.value = new mapboxgl.Map({
        container: "mapContainer",
        style: "mapbox://styles/foundryspatial/clkrhe0yc009j01pufslzevl4",
        center: { lat: 55, lng: -125.6 },
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
    map.value.addControl(
        new mapboxgl.NavigationControl({ showCompass: false }),
        "bottom-right"
    );
    map.value.on("load", () => {
        emit("loaded", map.value);
    });
});
</script>
