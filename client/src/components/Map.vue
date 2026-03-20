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
import { customAttribution, loadMapBounds, saveMapBounds } from '@/utils/mapHelpers.js';
import { onMounted, ref } from "vue";
import mapboxgl from "mapbox-gl";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { env } from '@/env'

const emit = defineEmits(["loaded"]);

const map = ref(null);

const props = defineProps({
    loading: {
        type: Boolean,
        default: false,
    },
    currentSection: {
        type: String,
        default: "",
    },
    preserveDrawingBuffer: {
        type: Boolean,
        default: false,
    }
});

/**
 * Create MapBox map. Add universal map controls. Emit to the parent component for page specific setup
 */
onMounted(() => {
    mapboxgl.accessToken = env.VITE_APP_MAPBOX_TOKEN;

    const baseMapWatershed = 'mapbox://styles/bcwatertool/cmds0uj4o007101re4ywuha95'
    const satelliteWatershed = 'mapbox://styles/bcwatertool/cme0m08mc00ok01spdki20gyb';
    const baseMapOthers = 'mapbox://styles/bcwatertool/cmds0s61z005j01sr0ajibjxm';
    const satelliteOthers = 'mapbox://styles/bcwatertool/cme0lx2tt00hu01reas1fcfjl';

    const baseMap = props.currentSection === 'watershed' ? baseMapWatershed : baseMapOthers;
    const satellite = props.currentSection === 'watershed' ? satelliteWatershed : satelliteOthers;

    const savedBounds = loadMapBounds();
    if (savedBounds !== null) {
        map.value = new mapboxgl.Map({
            container: "mapContainer",
            style: baseMap,
            bounds: savedBounds,
            attributionControl: false,
            preserveDrawingBuffer: props.preserveDrawingBuffer,
            logoPosition: "bottom-left",
        });
    } else {
        map.value = new mapboxgl.Map({
            container: "mapContainer",
            style: baseMap,
            center: { lat: 55, lng: -125.6 },
            zoom: 5,
            attributionControl: false,
            preserveDrawingBuffer: props.preserveDrawingBuffer,
            logoPosition: "bottom-left",
        });
    }

    map.value.addControl(new maplibregl.AttributionControl({ customAttribution }));

    if (props.scaleControl) {
        map.value.addControl(new mapboxgl.ScaleControl(), "bottom-right");
    }
    // Map Style Control (street || satellite)
    const mapStyleControl = {
        onAdd(map) {
            const forEachLayer = (text, cb) => {
                map.getStyle().layers.forEach((layer) => {
                    if (!layer.id.includes(text)) return;

                    cb(layer);
                });
            }
            const container = document.createElement('div');
            container.className = 'mapboxgl-ctrl mapboxgl-ctrl-group';
            container.innerHTML = `
                <button aria-diabled="false" type="button" class="satellite-button line" id="satellite" />
                <button aria-diabled="false" type="button" class="earth-button" id="street" />`;
            container.addEventListener('click', (e) => {
                if (!map.isStyleLoaded()) return;
                const savedLayers = [];
                const savedSources = {};
                const layerGroups = [
                    'point-layer',
                    'highlight-layer',
                    'polygon-layer'
                ];

                layerGroups.forEach((layerGroup) => {
                    forEachLayer(layerGroup, (layer) => {
                        savedSources[layer.source] = map.getSource(layer.source).serialize();
                        savedLayers.push(layer);
                    });
                });
                if (e.target.id === "satellite") {
                    map.setStyle(satellite);
                } else if (e.target.id === "street") {
                    map.setStyle(baseMap);
                }

                setTimeout(() => {
                    Object.entries(savedSources).forEach(([id, source]) => {
                        if (!map.getSource(id)) map.addSource(id, source);
                    });

                    savedLayers.forEach((layer) => {
                        if (!map.getLayer(layer.id)) map.addLayer(layer);
                    });
                }, 500);
                return;
            });
            return container;
        },
        onRemove() {
            return;
        }
    };
    if (props.styleControl) {
        map.value.addControl(mapStyleControl, 'bottom-right');
    }

    if (props.navControl) {
        map.value.addControl(new mapboxgl.NavigationControl({ showCompass: true }), 'bottom-right');
    }
    map.value.on("load", () => {
        emit("loaded", map.value);
    });
    map.value.on('moveend', () => {
        saveMapBounds(map.value)
    });

    window.map = map.value;
});
</script>

<style lang="scss">
.earth-button {
    background: linear-gradient(45deg, #e7ebe2 50%, #dae6ca 50%);
}

.satellite-button {
    background: linear-gradient(45deg, #14202d 50%, #314720 50%);
}

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
