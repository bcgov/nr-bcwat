<template>
    <div class="report-break">
        <div class="spaced-flex-row report-header">
            <div>
                <h1>Watershed Summary</h1>
                <h2>{{ props.reportContent.overview.watershedName }} (WFI: {{ props.wfi }})</h2>
            </div>
            <div class="location-timeline">
                <q-timeline>
                    <q-timeline-entry
                        v-for="(item, index) in props.reportContent.overview.busStopNames"
                        :key="index"
                        :title="item"
                        :color="index === 0 ? 'orange' : ''"
                        layout="dense"
                        side="right"
                    />
                </q-timeline>
            </div>
        </div>
        <div class="watershed-report-map">
            <section id="watershed-report-map-container" class="watershed-report-map-container" />
        </div>
        <hr class="q-my-xl"/>
    </div>
</template>
<script setup>
import mapboxgl from "mapbox-gl";
import { env } from '@/env'
import { onMounted, ref } from "vue";

const props = defineProps({
    reportContent: {
        type: Object,
        default: () => {},
    },
    points: {
        type: Array,
        default: () => [],
    },
    wfi: {
        type: String,
        default: '',
    }
});

const map = ref(null);

onMounted(() => {
    mapboxgl.accessToken = env.VITE_APP_MAPBOX_TOKEN;
    map.value = new mapboxgl.Map({
        container: "watershed-report-map-container",
        style: "mapbox://styles/bcwatertool/cmds0uj4o007101re4ywuha95",
        center: {
            lat: props.reportContent.overview.mgmt_lat,
            lng: props.reportContent.overview.mgmt_lng,
        },
        zoom: 9,
        attributionControl: false,
        logoPosition: "bottom-left",
        preserveDrawingBuffer: true,
    });
    map.value.scrollZoom.disable();
    // Add map layers and points
    map.value.on("load", () => {
        // Add map layers and points
        if (!map.value.getSource("point-source")) {
            const featureJson = {
                type: "geojson",
                data: props.points,
            };
            map.value.addSource("point-source", featureJson);
        }
        if (!map.value.getLayer("point-layer")) {
            map.value.addLayer(pointLayer, "poi-islands");
            map.value.setPaintProperty("point-layer", "circle-color", [
                "match",
                ["get", "type"],
                "SW",
                "#61913d",
                "GW",
                "#234075",
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
        
        if (!map.value.getSource("query-watershed-source")) {
            // Add polygon for user selected polygon
            map.value.addSource("query-watershed-source", {
                type: "geojson",
                data: {
                    type: "Feature",
                    geometry: props.reportContent.overview.query_polygon,
                },
            });
            map.value.addLayer({
                id: "watershed-layer",
                type: "fill",
                source: "query-watershed-source",
                paint: {
                    "fill-color": "#f26721",
                    "fill-opacity": 0.5,
                },
            });
        }
    }); 
});

</script>

<style lang="scss">
.watershed-report-map {
    display: none;
}
</style>
