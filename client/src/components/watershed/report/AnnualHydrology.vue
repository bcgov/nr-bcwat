<template>
    <div>
        <h1 class="q-mb-md">Annual Hydrology</h1>
        <p>
            This section describes the annual water supply and demand, for the
            location (Halden Creek) that you selected. The watershed is outlined
            in orange on the map below. The watershed associated with the next
            downstream confluence (Halden Creek (Downstream)) has also been
            outlined in purple, with summary statistics for both watersheds
            provided in the table below. Please note that all values presented
            are estimates and are subject to error.
        </p>
        <div class="annual-hydrology-map">
            <section id="ahMapContainer" class="map-container" />
        </div>

        <pre>{{ Object.keys(props.reportContent) }}</pre>
        <hr />
        <pre>{{ Object.keys(props.reportContent.overview) }}</pre>

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
                                .query).toFixed(0)
                        }}
                    </td>
                    <td>
                        {{
                            (+props.reportContent.annualHydrology.area_km2
                                .downstream).toFixed(0)
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
                    <td>Allocations (average, m<sup>3</sup>/yr)</td>
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
                        {{
                            (+props.reportContent.annualHydrology.allocs_pct
                                .query).toFixed(1)
                        }}
                    </td>
                    <td>
                        {{
                            (+props.reportContent.annualHydrology.allocs_pct
                                .downstream).toFixed(1)
                        }}
                    </td>
                </tr>
                <tr>
                    <td>Reserves & Restrictions</td>
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
                            (+props.reportContent.annualHydrology.allocs_m3s
                                .query).toFixed(0)
                        }}
                    </td>
                    <td>
                        {{
                            (+props.reportContent.annualHydrology.allocs_m3s
                                .downstream).toFixed(0)
                        }}
                    </td>
                </tr>
                <tr>
                    <td>Seasonal Flow Sensitivity</td>
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
        <hr />
    </div>
</template>

<script setup>
import { annualHydrologyLayer } from "@/constants/mapLayers.js";
import { addCommas } from "@/utils/stringHelpers.js";
import { onMounted, ref } from "vue";
import foundryLogo from "@/assets/foundryLogo.svg";
import mapboxgl from "mapbox-gl";

const map = ref(null);

/**
 * Create MapBox map. Add universal map controls. Emit to the parent component for page specific setup
 */
onMounted(() => {
    mapboxgl.accessToken = import.meta.env.VITE_APP_MAPBOX_TOKEN;
    map.value = new mapboxgl.Map({
        container: "ahMapContainer",
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
        if (!map.value.getSource("annual-hydrology-source")) {
            map.value.addSource("annual-hydrology-source", {
                type: "geojson",
                data: {
                    type: "Feature",
                    geometry: props.reportContent.overview.query_polygon,
                },
            });
            map.value.addLayer(annualHydrologyLayer);
        }
    });
});

const props = defineProps({
    reportContent: {
        type: Object,
        default: () => {},
    },
});
</script>

<style lang="scss">
.annual-hydrology-map {
    display: grid;
    min-height: 40vh;
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
    }
}
</style>
