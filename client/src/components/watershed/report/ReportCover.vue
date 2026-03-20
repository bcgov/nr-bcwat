<template>
  <StaticReportCover
    :title="userTitle"
    :name-subtitle="watershedName"
    :id-subtitle="`Watershed Number: ${props.wfi}`"
  >
    <div class="report-map">
        <div 
            id="watershedReportCoverMapContainer" 
            class="report-cover-map-container"
            ref="watershed-report-cover-map-container"
        />
        <img
            class="watershed-report-map-image"
            :class="props.isReport ? 'report' : ''"
            :src="mapSrc"
        />
    </div>
  </StaticReportCover>
</template>

<script setup>
import html2canvas from "html2canvas";
import mapboxgl from "mapbox-gl";
import StaticReportCover from "@/components/watershed/report/StaticReportCover.vue";
import { env } from "@/env.js";
import { pointLayer } from "@/constants/mapLayers.js";
import { useRoute } from "vue-router";
import { reportFileName } from "@/utils/reportHelpers.js";
import { computed, ref, onMounted, useTemplateRef } from "vue";

const route = useRoute();

const props = defineProps({
  reportContent: {
    type: Object,
    required: true,
  },
  points: {
    type: Object,
    default: () => {},
  },
  wfi: {
    type: String,
    default: ''
  }
});

const emit = defineEmits(["load"]);

const map = ref(null);
const mapSrc = ref(null);
const mapContainer = useTemplateRef("watershed-report-cover-map-container");

const watershedName = computed(() => {
  return route.query.watershedName;
});

const userTitle = computed(() => {
  return reportFileName(props.reportContent.userCustomization.userTitle);
});

onMounted(() => {
    mapboxgl.accessToken = env.VITE_APP_MAPBOX_TOKEN;
    map.value = new mapboxgl.Map({
        container: "watershedReportCoverMapContainer",
        style: 'mapbox://styles/bcwatertool/cmds0uj4o007101re4ywuha95',
        center: {
            lat: props.reportContent.overview.mgmt_lat,
            lng: props.reportContent.overview.mgmt_lng,
        },
        zoom: 9,
        preserveDrawingBuffer: true,
        attributionControl: false,
        logoPosition: "bottom-left",
    });

    map.value.addControl(
        new mapboxgl.AttributionControl({
            customAttribution: `<a target="_blank" href="https://www.foundryspatial.com/">
                <img style="margin: -3px 0 -3px 2px; width: 15px; height: 15px;" src="/foundryLogo.svg">
            </a>`,
        })
    );

    map.value.addControl(new mapboxgl.ScaleControl(), "bottom-left");

    map.value.on("load", async () => {
        initialize(map.value);
    });

    map.value.on("idle", async () => {
        const mapEl = await html2canvas(mapContainer.value, { 
            logging: false,
            scale: 2
        });
        mapSrc.value = mapEl.toDataURL();
        document.reportCoverLoaded = true;
    });
});

/**
 * Initialize the map element
 *
 * @param {Event} ev - the event received from the map when it's initialized
 * @param {mapboxgl.Map} mapObj - Mapbox GL map object
 */
const initialize = (mapObj) => {
    setView(mapObj);
    addLayers(mapObj);
    emit("load");
};

/**
 * Position the given map
 *
 * @param {mapboxgl.Map} mapObj - Mapbox GL map object
 */
const setView = (mapObj) => {
  // fit to bounding box of the watershed polygon
  const bounds = new mapboxgl.LngLatBounds();
  props.reportContent.overview.query_polygon.coordinates[0].forEach((coord) => {
    bounds.extend(coord);
  });

  mapObj.fitBounds(bounds, {
    padding: 50,
    animate: false,
  });
};

/**
 * Add watershed polygon
 *
 * @param {mapboxgl.Map} mapObj - Mapbox GL map object
 */
const addLayers = (mapObj) => {
  mapObj.addLayer({
    id: "watershed-polygon",
    type: "fill",
    source: {
      type: "geojson",
      data: props.reportContent.overview.query_polygon,
    },
    layout: {},
    paint: {
      "fill-color": "#FFA500",
      "fill-opacity": 0.5,
      "fill-outline-color": "#FFA800",
    },
  });

  if (!mapObj.getSource("point-source")) {
    const featureJson = {
      type: "geojson",
      data: props.points,
    };
    mapObj.addSource("point-source", featureJson);
  }

  if (!mapObj.getLayer("point-layer")) {
    mapObj.addLayer(pointLayer);
    mapObj.setPaintProperty("point-layer", "circle-color", [
      "match",
      ["get", "type"],
      "SW",
      "#61913d",
      "GW",
      "#283593",
      "#ccc",
    ]);

    mapObj.setPaintProperty("point-layer", "circle-stroke-color", [
      "match",
      ["get", "st"],
      "ACTIVE APPL.",
      "#FAA500",
      "#fff",
    ]);
  }
};
</script>
<style lang="scss">
.report-map {
    position: relative;
    flex: 1;
    height: 460px;
    width: 640px;
    margin-top: 2rem;
    margin-left: auto;
    margin-right: auto;

    .watershed-report-map-image {
        position: absolute;
        top: 0;
        left: 0;
        display: flex;
        width: 100%;
        height: 30rem;
        z-index: 2;
    }
}

.report-cover-map-container {
    height: 30rem;
}
</style>
