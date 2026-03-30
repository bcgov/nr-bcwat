<template>
  <div>
    <div class="report-break">
        <div :class="props.isReport ? 'report-section-header' : ''">
            <div class="text-h4 q-my-lg">Annual Water Supply and Demand</div>
        </div>
      <p>
        This section describes the annual water supply and demand, for the
        location ({{ props.reportContent.overview.watershedName }}) that you
        selected. The watershed is outlined in orange on the map below. The
        watershed associated with the next downstream confluence<NoteLink
          :note-number="2"
        />
        ({{ props.reportContent.overview.mgmt_name }}) has also been outlined in
        purple, with summary statistics for both watersheds provided in the
        table below. Please note that all values presented are estimates and are
        subject to error<NoteLink :note-number="3" />.
      </p>
      <div class="annual-hydrology-map">
            <div
                class="watershed-report-map"
                :class="props.isReport ? 'report' : ''"
            >
            <div
                id="annualHydrologyMapContainer"
                class="report-map-container"
                ref="annual-hydrology-map-container"
            />
        </div>
        <img
            class="annual-hydrology-map-image"
            :class="props.isReport ? 'report' : ''"
            :src="mapSrc"
        />
      </div>
      <div class="annual-hydrology-map-legend">
        <div>
          <MapMarker fill="#cc5207" />
          Query Watershed
        </div>
        <div>
          <MapMarker fill="#1e1436" />
          Downstream Watershed
        </div>
      </div>

      <table class="annual-hydrology-table">
        <tbody>
          <tr>
            <th>Annual Statistics</th>
            <th>{{ reportContent.overview.watershedName }}</th>
            <th>
              {{ reportContent.overview.mgmt_name }}
            </th>
          </tr>
          <tr>
            <td>Area (km<sup>2</sup>)</td>
            <td>
              {{
                handleDecimalPlaces(
                  +props.reportContent.annualHydrology.area_km2.query,
                  3,
                )
              }}
            </td>
            <td>
              {{
                handleDecimalPlaces(
                  +props.reportContent.annualHydrology.area_km2.downstream,
                  3,
                )
              }}
            </td>
          </tr>
          <tr>
            <td>Mean Annual Discharge (MAD, m³/s)</td>
            <td>
              {{
                handleDecimalPlaces(
                  +props.reportContent.annualHydrology.mad_m3s.query,
                  3,
                )
              }}
            </td>
            <td>
              {{
                handleDecimalPlaces(
                  +props.reportContent.annualHydrology.mad_m3s.downstream,
                  3,
                )
              }}
            </td>
          </tr>
          <tr>
            <td>
              Allocations (average, m³/s)<NoteLink
                :note-number="9"
              />
            </td>
            <td>
              {{
                handleDecimalPlaces(
                  +props.reportContent.annualHydrology.allocs_m3s.query,
                  3,
                )
              }}
            </td>
            <td>
              {{
                handleDecimalPlaces(
                  +props.reportContent.annualHydrology.allocs_m3s.downstream,
                  3,
                )
              }}
            </td>
          </tr>
          <tr>
            <td>Allocations (average, % of MAD)</td>
            <td>
              {{
                handleDecimalPlaces(
                  +props.reportContent.annualHydrology.allocs_pct.query,
                  5,
                )
              }}
            </td>
            <td>
              {{
                handleDecimalPlaces(
                  +props.reportContent.annualHydrology.allocs_pct.downstream,
                  5,
                )
              }}
            </td>
          </tr>
          <tr>
            <td>Reserves & Restrictions<NoteLink :note-number="4" /></td>
            <td>{{ props.reportContent.annualHydrology.rr.query }}</td>
            <td>
              {{ props.reportContent.annualHydrology.rr.downstream }}
            </td>
          </tr>
          <tr>
            <td>Volume Runoff (m³/yr)</td>
            <td>
              {{
                handleDecimalPlaces(
                  +props.reportContent.annualHydrology.runoff_m3yr.query,
                  0,
                )
              }}
            </td>
            <td>
              {{
                handleDecimalPlaces(
                  +props.reportContent.annualHydrology.runoff_m3yr.downstream,
                  0,
                )
              }}
            </td>
          </tr>
          <tr>
            <td>Volume Allocations (m³/yr)</td>
            <td>
              {{
                handleDecimalPlaces(
                  +props.reportContent.annualHydrology.allocs_m3yr.query,
                  0,
                )
              }}
            </td>
            <td>
              {{
                handleDecimalPlaces(
                  +props.reportContent.annualHydrology.allocs_m3yr.downstream,
                  0,
                )
              }}
            </td>
          </tr>
          <tr>
            <td>Seasonal Flow Sensitivity<NoteLink :note-number="5" /></td>
            <td>
              {{ props.reportContent.annualHydrology.seasonal_sens.query }}
            </td>
            <td>
              {{ props.reportContent.annualHydrology.seasonal_sens.downstream }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <q-separator class="q-my-xl" />
  </div>
</template>

<script setup>
import MapMarker from "@/components/watershed/report/MapMarker.vue";
import NoteLink from "@/components/watershed/report/NoteLink.vue";
import { customAttribution } from "@/utils/mapHelpers.js";
import { handleDecimalPlaces } from "@/utils/stringHelpers.js";
import { onMounted, ref, useTemplateRef } from "vue";
import { pointLayer } from "@/constants/mapLayers.js";
import { env } from '@/env';
import html2canvas from "html2canvas";
import maplibregl from "maplibre-gl";
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
  points: {
    type: Object,
    default: () => {},
  },
  isReport: {
    type: Boolean,
    default: false,
  },
});

const queryWatershedMarker = ref(null);
const downstreamMarker = ref(null);
const map = ref(null);
const mapSrc = ref("");
const mapContainer = useTemplateRef("annual-hydrology-map-container");

/**
 * Create MapBox map. Add universal map controls. Emit to the parent component for page specific setup
 */
onMounted(async () => {
    mapboxgl.accessToken = env.VITE_APP_MAPBOX_TOKEN;
    map.value = new maplibregl.Map({
        container: "annualHydrologyMapContainer",
        style: `mapbox://styles/bcwatertool/cmds0uj4o007101re4ywuha95`,
        center: {
            lat: props.reportContent.overview.mgmt_lat,
            lng: props.reportContent.overview.mgmt_lng,
        },
        zoom: 9,
        preserveDrawingBuffer: true,
        attributionControl: false,
        logoPosition: "bottom-left",
        interactive: false,
    });
    map.value.addControl(new maplibregl.AttributionControl({ customAttribution }));
    map.value.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'bottom-right');
    map.value.addControl(new maplibregl.ScaleControl(), "bottom-left");
    map.value.on("load", async () => {
        // Add map layers and points
        if (!map.value.getSource("point-source")) {
            const featureJson = {
                type: "geojson",
                data: props.points,
            };
            map.value.addSource("point-source", featureJson);
        }

        if (!map.value.getLayer("point-layer")) {
            map.value.addLayer(pointLayer);
            map.value.setPaintProperty("point-layer", "circle-color", [
                "match",
                ["get", "type"],
                "SW",
                "#61913d",
                "GW",
                "#283593",
                "#ccc",
            ]);
        }

        if (!map.value.getSource("query-polygon-source")) {
            map.value.addSource("query-polygon-source", {
                type: "geojson",
                data: {
                    type: "Feature",
                    geometry: props.reportContent.overview.query_polygon,
                },
            });
            map.value.addLayer({
                id: "watershed-layer",
                type: "fill",
                source: "query-polygon-source",
                paint: {
                    "fill-color": "#f26721",
                    "fill-opacity": 0.5,
                },
            });
            map.value.addLayer({
                id: "watershed-line-layer",
                type: "line",
                source: "query-polygon-source",
                paint: {
                    "line-color": "#cc5207",
                },
            });
        }

        if (!map.value.getSource("annual-hydrology-source")) {
            map.value.addSource("downstream-source", {
                type: "geojson",
                data: {
                    type: "Feature",
                    geometry: props.reportContent.overview.mgmt_polygon,
                },
            });
            map.value.addLayer({
                id: "downstream-layer",
                type: "fill",
                source: "downstream-source",
                paint: {
                    "fill-color": "#3d3254",
                    "fill-opacity": 0.5,
                },
            });
            map.value.addLayer({
                id: "downstream-line-layer",
                type: "line",
                source: "downstream-source",
                paint: {
                    "line-color": "#1e1436",
                },
            });

            if(!queryWatershedMarker.value){
                queryWatershedMarker.value = new maplibregl.Marker({ color: "#cc5207" })
                    .setLngLat([
                        props.clickedPoint?.lng || props.reportContent.lngLat.lng,
                        props.clickedPoint?.lat || props.reportContent.lngLat.lat,
                    ])
                    .addTo(map.value);
            }

            if(!downstreamMarker.value){
                downstreamMarker.value = new maplibregl.Marker({ color: "#1e1436" })
                    .setLngLat([
                        props.reportContent.overview.mgmt_lng,
                        props.reportContent.overview.mgmt_lat,
                    ])
                    .addTo(map.value);
            }
        }

        map.value.on("idle", async () => {
            if(mapContainer.value){
                // const els = document.getElementsByClassName("maplibregl-ctrl-logo");
                // els.forEach(el => {
                //   el.style.display = 'none';
                // })
                const mapEl = await html2canvas(mapContainer.value, { logging: false });
                mapSrc.value = mapEl.toDataURL();
                document.annualHydrologyLoaded = true;
            }
        });
    });

    // fit to bounding box of the watershed polygon
    const bounds = new maplibregl.LngLatBounds();
    props.reportContent.overview.mgmt_polygon.coordinates[0].forEach((coord) => {
        bounds.extend(coord);
    });

    map.value.fitBounds(bounds, {
        padding: 50,
        animate: false,
    });
});
</script>

<style lang="scss">
.annual-hydrology-map {
    position: relative;
    min-height: 23rem;

    .annual-hydrology-map-image {
        position: absolute;
        top: 0;
        left: 0;
        display: none;
        width: 100%;
        z-index: 2;

        &.report {
            display: grid;
        }
    }
    .watershed-report-map {
        display: grid;
        z-index: 1;
        min-height: 23rem;

        &.report {
            height: 0;
        }
    }
}

.annual-hydrology-map-legend {
  background-color: $light-grey-accent;
  display: flex;
  margin-bottom: 2em;

  div {
    align-items: center;
    display: flex;
    padding: 0.5em;
    justify-content: center;
    width: 50%;
    svg {
      max-height: 30px;
      margin-right: 1em;
    }
  }
}
.annual-hydrology-table {
  border-collapse: collapse;
  margin-bottom: 5em;
  width: 100%;

  tr {
    border-bottom: 1pt solid $primary-font-color;
    text-align: end;

    :first-child {
      text-align: start;
    }

    &:last-child {
      border-bottom: unset;
    }

    td,
    th {
      padding: 0.5em;
    }
  }
}
</style>
