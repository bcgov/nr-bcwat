<template>
    <div class="page-container">
        <section id="mapContainer" ref="mapContainer" class="map-container" />
    </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import foundryLogo from "@/assets/foundryLogo.svg";
import mapboxgl from "mapbox-gl";

const map = ref(null);
const mapContainer = ref();

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
});
</script>

<!-- Cannot leave style tag out without breaking map for some reason -->
<style lang="scss" scoped>
.map {
    height: auto;
}
</style>
