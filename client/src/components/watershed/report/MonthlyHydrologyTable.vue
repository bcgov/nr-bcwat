<template>
    <div id="monthly-hydrology-table" class="monthly-hydrology-table">
        <q-table
            :rows="['']"
            :columns="tableCols"
            :pagination="{ rowsPerPage: 0 }"
            hide-pagination
            dense
            flat
            wrap-cells
        >
            <template #body>
                <q-tr>
                    <q-td>
                        % of MAD
                    </q-td>
                    <q-td v-for="month in props.monthlyHydrology.monthlyDischargePercentages">
                        {{ parseFloat(month).toFixed(2) }}
                    </q-td>
                </q-tr>
                <q-tr>
                    <q-td>Flow Sensitivity</q-td>
                    <q-td v-for="(_, idx) in monthAbbrList" :key="idx">
                        {{ props.monthlyHydrology.monthlyFlowSensitivities[idx] }}
                    </q-td>
                </q-tr>
                <q-tr>
                    <q-td>Existing Water Licences* (m³/s)</q-td>
                    <q-td v-for="(_, idx) in monthAbbrList" :key="idx">
                        <span
                            :title = props.monthlyHydrology.waterLicenceMonthlyDisplay[idx]
                        >
                        {{ handleDecimalPlaces(+props.monthlyHydrology.waterLicenceMonthlyDisplay[idx], 2) }}
                        </span>
                    </q-td>
                </q-tr>
                <q-tr>
                    <q-td>Existing Short Term Approvals* (m³/s)</q-td>
                    <q-td v-for="(_, idx) in monthAbbrList" :key="idx">
                        <span
                            :title = props.monthlyHydrology.shortTermAllocationMonthlyDisplay[idx]
                        >
                        {{ handleDecimalPlaces(+props.monthlyHydrology.shortTermAllocationMonthlyDisplay[idx], 2) }}
                        </span>
                    </q-td>
                </q-tr>
                <q-tr>
                    <td>Mean Monthly Discharge (m³/s)</td>
                    <td v-for="(_, idx) in monthAbbrList" :key="idx">
                        <span
                            :title = props.monthlyHydrology.monthlyDischarge[idx]
                        >
                            {{ handleDecimalPlaces(+props.monthlyHydrology.monthlyDischarge[idx], 2) }}
                        </span>
                    </td>
                </q-tr>
                <q-tr>
                    <td>Potential Allocation (m³/s, Risk Mgmt 1)</td>
                    <td v-for="(_, idx) in monthAbbrList" :key="idx">
                        <span
                            :title = props.monthlyHydrology.rm1[idx]
                        >
                            {{ handleDecimalPlaces(+props.monthlyHydrology.rm1[idx], 2) }}
                        </span>
                    </td>
                </q-tr>
                <q-tr>
                    <td>Potential Allocation (m³/s, Risk Mgmt 2)</td>
                    <td v-for="(_, idx) in monthAbbrList" :key="idx">
                        <span
                            :title = props.monthlyHydrology.rm2[idx]
                        >
                            {{ handleDecimalPlaces(+props.monthlyHydrology.rm2[idx], 2) }}
                        </span>
                    </td>
                </q-tr>
                <q-tr>
                    <td>Potential Allocation (m³/s, Risk Mgmt 3)</td>
                    <td v-for="(_, idx) in monthAbbrList" :key="idx">
                        <span
                            :title = props.monthlyHydrology.rm3[idx]
                        >
                        {{ props.monthlyHydrology.rm3[idx].slice(0, 1) }} {{ addCommas((+props.monthlyHydrology.rm3[idx].slice(1)).toFixed(2)) }}
                         </span>
                    </td>
                </q-tr>
            </template>
        </q-table>
    </div>
</template>

<script setup>
import { monthAbbrList } from "@/utils/dateHelpers";
import { addCommas, handleDecimalPlaces } from "@/utils/stringHelpers";
import { onMounted } from "vue";

const props = defineProps({
    monthlyHydrology: {
        type: Object,
        default: () => {},
    },
});

onMounted(() => {
    console.log(props.monthlyHydrology)
})

const tableCols = [
    {
        name: 'title',
        field: '',
    },
    { name: 'jan', label: 'Jan', align: 'center' },
    { name: 'feb', label: 'Feb', align: 'center' },
    { name: 'mar', label: 'Mar', align: 'center' },
    { name: 'apr', label: 'Apr', align: 'center' },
    { name: 'may', label: 'May', align: 'center' },
    { name: 'jun', label: 'Jun', align: 'center' },
    { name: 'jul', label: 'Jul', align: 'center' },
    { name: 'aug', label: 'Aug', align: 'center' },
    { name: 'sep', label: 'Sep', align: 'center' },
    { name: 'oct', label: 'Oct', align: 'center' },
    { name: 'nov', label: 'Nov', align: 'center' },
    { name: 'dec', label: 'Dec', align: 'center' },
]
</script>

<style lang="scss">
.monthly-hydrology-table {
    width: fit-content;
    overflow-x: auto;

    table {
        tr {
            &:nth-child(even) {
                background-color: $light-grey-accent;
            }
        }

        th {
            font-weight: bold;
        }

        td,
        th {
            font-size: 12px;
            text-align: end;

            &:first-child {
                font-weight: bold;
                word-break: normal;
                text-align: start;
            }
        }
    }
}
</style>
