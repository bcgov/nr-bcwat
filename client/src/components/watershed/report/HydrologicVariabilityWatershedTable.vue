<template>
    <div id="hydrologic-watershed-table">
        <q-table
            :rows="props.tableData"
            :columns="tableCols"
            :pagination="{ rowsPerPage: 0 }"
            hide-pagination
            flat
            wrap-cells
        >
            <template #header="props">
                <q-tr 
                    :props="props"
                >
                    <q-th />
                    <q-th>
                        <div class="header">Watershed</div>
                    </q-th>
                    <q-th>
                        <div class="header">Location</div> 
                        <div class="text-italic">(lat, lng)</div>
                    </q-th>
                    <q-th>
                        <div class="header">Area</div>
                        <div class="text-italic">(km²)</div>
                    </q-th>
                    <q-th>
                        <div class="header">Elevation</div>
                        <div class="text-italic">(m: min, mean, max)</div>
                    </q-th>
                    <q-th>
                        <div class="header">Precipitation</div>
                        <div class="text-italic">(mm/mo)</div>
                    </q-th>
                    <q-th>
                        <div class="header">Precip. as snow</div>
                        <div class="text-italic">(mm/mo)</div>
                    </q-th>
                    <q-th>
                        <div class="header">Temperature</div>
                        <div class="text-italic">(°C)</div>
                    </q-th>
                </q-tr>
            </template>
            <template #body="props">
                <q-tr :props="props">
                    <q-td class="circle-cell">
                        <div
                            class="legend-circle"
                            :style="{
                                'background-color':
                                    hydrologicWatershedColors[
                                        (props.rowIndex - 1) % 8
                                    ],
                            }"
                        />
                    </q-td>
                    <q-td>
                        <div class="text-capitalize text-bold">
                            {{ props.row.type }} watershed
                        </div>
                        <div>
                            {{ props.row.station_number }}
                        </div>
                        <div>
                            {{ props.row.station_name }}
                        </div>
                    </q-td>
                    <q-td>
                        {{ props.row.lat.toFixed(3) }}, {{ props.row.lng.toFixed(3) }}
                    </q-td>
                    <q-td>
                        {{ addCommas(props.row.area_km2.toFixed()) }}
                    </q-td>
                    <q-td>
                        {{ addCommas(props.row.min_elev.toFixed()) }}, 
                        {{ addCommas(props.row.avg_elev.toFixed()) }}, 
                        {{ addCommas(props.row.max_elev.toFixed()) }}
                    </q-td>
                    <q-td>
                        <HydrologicVariabilityLineChart
                            :chart-data="props.row.ppt"
                            :chart-id="`hydrologic-ppt-chart-${props.rowIndex}`"
                            data-cy="hydrologic-ppt-chart"
                            chart-type="Precip:"
                            color="#42a5f5"
                        />
                    </q-td>
                    <q-td>
                        <HydrologicVariabilityLineChart
                            :chart-data="props.row.pas"
                            :chart-id="`hydrologic-pas-chart-${props.rowIndex}`"
                            data-cy="hydrologic-pas-chart"
                            chart-type="Snow:"
                            color="#474748"
                        />
                    </q-td>
                    <q-td>
                        <HydrologicVariabilityLineChart
                            :chart-data="props.row.tave"
                            :chart-id="`hydrologic-tave-chart-${props.rowIndex}`"
                            data-cy="hydrologic-tave-chart"
                            chart-type="Temp:"
                            color="#f06825"
                        />
                    </q-td>
                </q-tr>
            </template>
        </q-table>
    </div>
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
        default: "",
    },
});

const tableCols = [
    {
        name: 'icon',
        field: '',
        label: '',
        align: 'left',
        sortable: false
    },
    { 
        name: 'Watershed',
        field: 'station_name',
        label: 'Watershed',
        sortable: false
    },
    { 
        name: 'location',
        field: 'lat',
        label: 'Location',
        sortable: false
    },
    { 
        name: 'area',
        field: 'area_km2',
        label: 'Area',
        sortable: false
    },
    { 
        name: 'precipitation',
        field: 'ppt',
        label: 'Precipitation',
        sortable: false
    },
    { 
        name: 'snow-precipitation',
        field: 'pas',
        label: 'Precip. as Snow',
        sortable: false
    },
    { 
        name: 'temperature',
        field: 'tave',
        label: 'Temperature',
        sortable: false
    }
]
</script>

<style lang="scss">
#hydrologic-watershed-table {
    width: 100%;

    td {
        padding: 0;

        .circle-cell {
            max-width: 1px !important;
        }
    }


    .legend-circle {
        border-radius: 50%;
        height: 15px;
        width: 15px;
    }

    th {
        text-wrap: unset;
        white-space-collapse: 'break-spaces';
        font-size: 14px;
        font-family: 'Roboto', sans-serif;

        .header {
            font-weight: bold;
        }
    }

    tr {
        td:first-child,
        th:first-child {
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


    .query-row {
        background-color: $light-grey-accent;
    }
}

</style>
