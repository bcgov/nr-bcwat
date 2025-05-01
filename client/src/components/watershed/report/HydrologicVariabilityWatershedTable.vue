<template>
    <table class="hydrologic-watershed-table">
        <tbody>
            <tr>
                <th>Watershed</th>
                <th>Location</th>
                <th>Area</th>
                <th>Elevation</th>
                <th>Precipitation</th>
                <th>Precip. as snow</th>
                <th>Temperature</th>
            </tr>
            <tr>
                <td></td>
                <td>(lat, long)</td>
                <td>(km<sup>2</sup>)</td>
                <td>(m: min, mean, max)</td>
                <td>(mm/mo)</td>
                <td>(mm/mo)</td>
                <td>(°C)</td>
            </tr>
            <tr
                v-for="(watershed, idx) in props.tableData"
                :key="idx"
                :class="idx === 0 ? 'wow' : ''"
            >
                <td class="border-bottom">
                    <table>
                        <tbody>
                            <tr>
                                <td></td>
                                <td><b>{{ watershed.station_name ? 'Candidate Watershed' : `Query Watershed`}}</b></td>
                            </tr>
                            <tr v-if="watershed.station_name">
                                <td class="flex">
                                    <span
                                        class="legend-circle"
                                        :style="{'background-color': hydrologicWatershedColors[(idx - 1) % 8]}"
                                    />
                                </td>
                                <td>
                                    {{ watershed.station_number }}
                                </td>
                            </tr>
                            <tr>
                                <td></td>
                                <td>{{ watershed.station_name || props.watershedName}}</td>
                            </tr>
                        </tbody>
                    </table>
                </td>
                <td class="border-bottom">
                    <div class="end-row">
                        <span>{{ watershed.lat.toFixed(3) }},</span>
                        {{ watershed.lng.toFixed(3) }}
                    </div>
                </td>
                <td class="border-bottom">{{ addCommas(watershed.area_km2.toFixed(0)) }}</td>
                <td class="border-bottom">
                    <div class="end-row">
                        <span>{{ addCommas(watershed.min_elev.toFixed(0)) }},</span>
                        <span>{{ addCommas(watershed.avg_elev.toFixed(0)) }},</span>
                        {{ addCommas(watershed.max_elev.toFixed(0)) }}
                    </div>
                </td>
                <td class="border-bottom">
                    <HydrologicVariabilityLineChart
                        :chart-data="watershed.ppt"
                        :chart-id="`hydrologic-ppt-chart-${idx}`"
                        chart-type="Precip:"
                        color="#42a5f5"
                    />
                </td>
                <td class="border-bottom">
                    <HydrologicVariabilityLineChart
                        :chart-data="watershed.pas"
                        :chart-id="`hydrologic-pas-chart-${idx}`"
                        chart-type="Snow:"
                        color="#474748"
                    />
                </td>
                <td class="border-bottom">
                    <HydrologicVariabilityLineChart
                        :chart-data="watershed.tave"
                        :chart-id="`hydrologic-tave-chart-${idx}`"
                        chart-type="Temp:"
                        color="#f06825"
                    />
                </td>
            </tr>
        </tbody>
    </table>
</template>

<script setup>
import HydrologicVariabilityLineChart from "@/components/watershed/report/HydrologicVariabilityLineChart.vue";
import { hydrologicWatershedColors } from "@/utils/constants.js";
import { addCommas } from "@/utils/stringHelpers.js";

const props = defineProps({
    tableData: {
        type: Object,
        default: () => {},
    },
    watershedName: {
        type: String,
        default: '',
    },
});

</script>

<style lang="scss">
.hydrologic-watershed-table {
    border-collapse: collapse;
    width: 100%;
    text-align: center;

    tr {
        td:first-child, th:first-child {
            text-align: start;
        }
    }

    .border-bottom {
        border-bottom: 1px solid grey;
        padding-bottom: 1em;
    }
    tr {
        &:nth-child(2) {
            border-bottom: 2px solid grey;
        }
    }

    .end-row {
        display: flex;
        flex-direction: column;
        text-align: end;
    }

    .legend-circle {
        border-radius: 50%;
        margin-right: 0.5em;
        height: 20px;
        width: 20px;
    }

    .wow {
        background-color: $light-grey-accent;
    }
}
</style>
