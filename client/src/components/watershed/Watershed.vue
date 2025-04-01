<template>
    <div class="page-container">
        <section id="mapContainer" ref="mapContainer" class="map-container" />
    </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import mapboxgl from "mapbox-gl";

const map = ref(null);
const mapContainer = ref();

onMounted(() => {
    mapboxgl.accessToken = import.meta.env.VITE_APP_MAPBOX_TOKEN;
    map.value = new mapboxgl.Map({
        container: "mapContainer",
        style: "mapbox://styles/foundryspatial/clxas9ujl01pv01rb42xsdqvg",
        center: { lat: 49, lng: -123 },
        zoom: 9,
        attributionControl: false,
        logoPosition: "bottom-left",
    });
});
</script>

<style lang="scss" scoped>
p {
    font-size: $base-font-size;
}
</style>
