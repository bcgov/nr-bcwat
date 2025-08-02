<template>
    <div>
        <h1 class="q-my-lg">Annual Hydrology</h1>
        <p>
            This section describes the annual water supply and demand, for the
            location ({{ props.reportContent.overview.watershedName }}) that you
            selected. The watershed is outlined in orange on the map below. The
            watershed associated with the next downstream confluence<NoteLink
                :note-number="2"
            />
            ({{ props.reportContent.overview.watershedName }} (Downstream)) has
            also been outlined in purple, with summary statistics for both
            watersheds provided in the table below. Please note that all values
            presented are estimates and are subject to error<NoteLink
                :note-number="3"
            />.
        </p>
        <div class="watershed-report-map">
            <section id="hydrologyMapContainer" class="map-container" />
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
                        {{ reportContent.overview.watershedName }} (downstream)
                    </th>
                </tr>
                <tr>
                    <td>Area (km<sup>2</sup>)</td>
                    <td>
                        {{
                            (+props.reportContent.annualHydrology.area_km2
                                .query).toFixed(3)
                        }}
                    </td>
                    <td>
                        {{
                            (+props.reportContent.annualHydrology.area_km2
                                .downstream).toFixed(3)
                        }}
                    </td>
                </tr>
                <tr>
                    <td>Mean Annual Discharge (MAD, m<sup>3</sup>/yr)</td>
                    <td>
                        {{
                            (+props.reportContent.annualHydrology.mad_m3s
                                .query).toFixed(3)
                        }}
                    </td>
                    <td>
                        {{
                            (+props.reportContent.annualHydrology.mad_m3s
                                .downstream).toFixed(3)
                        }}
                    </td>
                </tr>
                <tr>
                    <td>
                        Allocations (average, m<sup>3</sup>/yr)<NoteLink
                            :note-number="9"
                        />
                    </td>
                    <td>
                        {{
                            (+props.reportContent.annualHydrology.allocs_m3s
                                .query).toFixed(3)
                        }}
                    </td>
                    <td>
                        {{
                            (+props.reportContent.annualHydrology.allocs_m3s
                                .downstream).toFixed(3)
                        }}
                    </td>
                </tr>
                <tr>
                    <td>Allocations (average, % of MAD)</td>
                    <td>
                        {{ props.reportContent.annualHydrology.allocs_pct.query }}
                    </td>
                    <td>
                        {{ props.reportContent.annualHydrology.allocs_pct.downstream }}
                    </td>
                </tr>
                <tr>
                    <td>
                        Reserves & Restrictions<NoteLink :note-number="4" />
                    </td>
                    <td>{{ props.reportContent.annualHydrology.rr.query }}</td>
                    <td>
                        {{ props.reportContent.annualHydrology.rr.downstream }}
                    </td>
                </tr>
                <tr>
                    <td>Volume Runoff (m<sup>3</sup>/yr)</td>
                    <td>
                        {{
                            addCommas(
                                (+props.reportContent.annualHydrology
                                    .runoff_m3yr.query).toFixed(0)
                            )
                        }}
                    </td>
                    <td>
                        {{
                            addCommas(
                                (+props.reportContent.annualHydrology
                                    .runoff_m3yr.downstream).toFixed(0)
                            )
                        }}
                    </td>
                </tr>
                <tr>
                    <td>Volume Allocations (m<sup>3</sup>/yr)</td>
                    <td>
                        {{
                            addCommas(
                                (+props.reportContent.annualHydrology.allocs_m3yr
                                .query).toFixed(0)
                            )
                        }}
                    </td>
                    <td>
                        {{
                            addCommas(
                                (+props.reportContent.annualHydrology.allocs_m3yr
                                .downstream).toFixed(0)
                            )
                        }}
                    </td>
                </tr>
                <tr>
                    <td>
                        Seasonal Flow Sensitivity<NoteLink :note-number="5" />
                    </td>
                    <td>
                        {{
                            props.reportContent.annualHydrology.seasonal_sens
                                .query
                        }}
                    </td>
                    <td>
                        {{
                            props.reportContent.annualHydrology.seasonal_sens
                                .downstream
                        }}
                    </td>
                </tr>
            </tbody>
        </table>
        <hr class="q-my-xl" />
    </div>
</template>

<script setup>
import MapMarker from "@/components/watershed/report/MapMarker.vue";
import NoteLink from "@/components/watershed/report/NoteLink.vue";
import { addCommas } from "@/utils/stringHelpers.js";
import { onMounted, ref } from "vue";
import foundryLogo from "@/assets/foundryLogo.svg";
import mapboxgl from "mapbox-gl";
import { env } from '@/env'

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

/**
 * Create MapBox map. Add universal map controls. Emit to the parent component for page specific setup
 */
onMounted(() => {
    mapboxgl.accessToken = env.VITE_APP_MAPBOX_TOKEN;
    map.value = new mapboxgl.Map({
        container: "hydrologyMapContainer",
        style: "mapbox://styles/foundryspatial/clkrhe0yc009j01pufslzevl4",
        center: {
            lat: props.reportContent.overview.mgmt_lat,
            lng: props.reportContent.overview.mgmt_lng,
        },
        zoom: 9,
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
            map.value.addSource("downstream-source", {
                type: "geojson",
                data: {
                    type: "Feature",
                    geometry: props.reportContent.overview.mgmt_polygon,
                },
            });
            map.value.scrollZoom.disable();
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
            map.value.addSource("annual-hydrology-source", {
                type: "geojson",
                data: {
                    type: "Feature",
                    geometry: props.reportContent.overview.query_polygon,
                },
            });
            map.value.addLayer({
                id: "watershed-layer",
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
                    "line-color": "#cc5207",
                },
            });

            new mapboxgl.Marker({ color: "#1e1436" })
                .setLngLat([
                    props.reportContent.overview.mgmt_lng,
                    props.reportContent.overview.mgmt_lat,
                ])
                .addTo(map.value);
            new mapboxgl.Marker({ color: "#cc5207" })
                .setLngLat([props.clickedPoint.lng, props.clickedPoint.lat])
                .addTo(map.value);
        }
    });

    // fit to bounding box of the watershed polygon
    const bounds = new mapboxgl.LngLatBounds();
    props.reportContent.overview.mgmt_polygon.coordinates[0].forEach(
        (coord) => {
            bounds.extend(coord);
        }
    );

    map.value.fitBounds(bounds, {
        padding: 50,
        animate: false,
    });
});
</script>

<style lang="scss">
.watershed-report-map {
    display: grid;
    min-height: 40vh;
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
