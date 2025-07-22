<template>
    <div 
        v-if="props.loading"
        class="map-loader-container"
    >
        <q-spinner 
            class="map-loader"
        />
    </div>
    <section id="mapContainer" class="map-container" />
</template>

<script setup>
import { onMounted, ref } from "vue";
import foundryLogo from "@/assets/foundryLogo.svg";
import mapboxgl from "mapbox-gl";
import { env } from '@/env'

const emit = defineEmits(["loaded"]);

const map = ref(null);

const props = defineProps({
    loading: {
        type: Boolean,
        default: false,
    }
});

/**
 * Create MapBox map. Add universal map controls. Emit to the parent component for page specific setup
 */
onMounted(() => {
    mapboxgl.accessToken = env.VITE_APP_MAPBOX_TOKEN;
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
    map.value.addControl(new mapboxgl.ScaleControl(), "bottom-right");
    map.value.addControl(new mapboxgl.NavigationControl({ showCompass: true }), 'bottom-right');
    map.value.on("load", () => {
        emit("loaded", map.value);
    });
});
</script>

<style lang="scss">
.map-loader-container {
    display: flex;
    position: absolute;
    align-items: center;
    justify-content: center;
    background-color: rgba(255, 255, 255, 0.3);
    top: 0;
    left: 0;
    z-index: 3;
    width: 100%;
    height: 100%;

    .map-loader {
        display: flex;
        position: absolute;
        height: 5rem;
        width: 5rem;
    }
}
</style>
