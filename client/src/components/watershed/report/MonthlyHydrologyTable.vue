<template>
    <div id="monthly-hydrology-table" class="monthly-hydrology-table report-table">
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
                    <q-td class="mad-col">
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
                    <q-td>
                        Existing Water Licences* 
                        <div>(m³/s)</div>
                    </q-td>
                    <q-td 
                        v-for="(_, idx) in monthAbbrList" :key="idx"
                    >
                        <span
                            v-if="+props.monthlyHydrology.waterLicenceMonthlyDisplay[idx] > 9999"
                            :title="props.monthlyHydrology.waterLicenceMonthlyDisplay[idx]"
                        >
                            {{ (+props.monthlyHydrology.waterLicenceMonthlyDisplay[idx]).toExponential(2).substring(0, 4) }}x10<sup>{{ (+props.monthlyHydrology.waterLicenceMonthlyDisplay[idx]).toExponential(2).substring(6, (+props.monthlyHydrology.waterLicenceMonthlyDisplay[idx]).toExponential(2).length) }}</sup>
                        </span>

                        <span
                            v-else
                            :title="props.monthlyHydrology.waterLicenceMonthlyDisplay[idx]"
                        >
                            {{ (+props.monthlyHydrology.waterLicenceMonthlyDisplay[idx]) }}
                        </span>
                    </q-td>
                </q-tr>
                <q-tr>
                    <q-td>
                        Existing Short Term Approvals*
                        <div>(m³/s)</div>
                    </q-td>
                    <q-td v-for="(_, idx) in monthAbbrList" :key="idx">
                        <span
                            :title = props.monthlyHydrology.shortTermAllocationMonthlyDisplay[idx]
                        >
                        {{ handleDecimalPlaces(+props.monthlyHydrology.shortTermAllocationMonthlyDisplay[idx], 2) }}
                        </span>
                    </q-td>
                </q-tr>
                <q-tr>
                    <td>
                        Mean Monthly Discharge
                        <div>
                            (m³/s)
                        </div>
                    </td>
                    <td v-for="(_, idx) in monthAbbrList" :key="idx">
                        <span
                            :title = props.monthlyHydrology.monthlyDischarge[idx]
                        >
                            {{ handleDecimalPlaces(+props.monthlyHydrology.monthlyDischarge[idx], 2) }}
                        </span>
                    </td>
                </q-tr>
                <q-tr>
                    <td>
                        Potential Allocation
                        <div>
                            (m³/s, Risk Mgmt 1)
                        </div>
                    </td>
                    <td v-for="(_, idx) in monthAbbrList" :key="idx">
                        <span
                            :title = props.monthlyHydrology.rm1[idx]
                        >
                            {{ handleDecimalPlaces(+props.monthlyHydrology.rm1[idx], 2) }}
                        </span>
                    </td>
                </q-tr>
                <q-tr>
                    <td>
                        Potential Allocation
                        <div>
                            (m³/s, Risk Mgmt 2)
                        </div>
                    </td>
                    <td v-for="(_, idx) in monthAbbrList" :key="idx">
                        <span
                            :title = props.monthlyHydrology.rm2[idx]
                        >
                            {{ handleDecimalPlaces(+props.monthlyHydrology.rm2[idx], 2) }}
                        </span>
                    </td>
                </q-tr>
                <q-tr>
                    <td>
                        Potential Allocation
                        <div>
                            (m³/s, Risk Mgmt 3)
                        </div>
                    </td>
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

const props = defineProps({
    monthlyHydrology: {
        type: Object,
        default: () => {},
    },
});
const tableCols = [
    {
        name: 'title',
        field: '',
    }, 
    ...monthAbbrList.map(el => {
        return {
            name: el,
            label: el,
            field: el,
            align: 'right',
        };
    })
];
</script>

<style lang="scss">
.monthly-hydrology-table {
    .existing-lic {
        word-wrap: break-word;
        word-break: break-all;
    }
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
            color: $table-font-color;
            font-family: 'BC Sans', sans-serif;
            text-align: end;

            &:first-child {
                font-weight: bold;
                text-align: start;
                width: 3rem;
            }
        }
    }
}
</style>
