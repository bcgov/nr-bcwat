<template>
    <div 
        id="monthly-hydrology-table" 
        class="monthly-hydrology-table"
        :class="props.isReport ? 'report' : ''"
    >
        <table>
            <tbody>
                <tr>
                    <th colspan="2"></th>
                    <th v-for="month in monthAbbrList" :key="month">
                        {{ month }}
                    </th>
                </tr>
                <tr>
                    <td colspan="2">% of MAD</td>
                    <td v-for="(_, idx) in monthAbbrList" :key="idx">
                        <span
                            :title = props.monthlyHydrology.monthlyDischargePercentages[idx]
                        >
                        {{ (+props.monthlyHydrology.monthlyDischargePercentages[idx]).toFixed(2) }}
                        </span>
                    </td>
                </tr>
                <tr>
                    <td colspan="2">Flow Sensitivity</td>
                    <td v-for="(_, idx) in monthAbbrList" :key="idx">
                        {{ props.monthlyHydrology.monthlyFlowSensitivities[idx] }}
                    </td>
                </tr>
                <tr>
                    <td colspan="2">Existing Water Licences* (m³/s)</td>
                    <td v-for="(_, idx) in monthAbbrList" :key="idx">
                        <span
                            :title = props.monthlyHydrology.waterLicenceMonthlyDisplay[idx]
                        >
                        {{ handleDecimalPlaces(+props.monthlyHydrology.waterLicenceMonthlyDisplay[idx], 2) }}
                        </span>
                    </td>
                </tr>
                <tr>
                    <td colspan="2">Existing Short Term Approvals* (m³/s)</td>
                    <td v-for="(_, idx) in monthAbbrList" :key="idx">
                        <span
                            :title = props.monthlyHydrology.shortTermAllocationMonthlyDisplay[idx]
                        >
                        {{ handleDecimalPlaces(+props.monthlyHydrology.shortTermAllocationMonthlyDisplay[idx], 2) }}
                        </span>
                    </td>
                </tr>
                <tr>
                    <td colspan="2">Mean Monthly Discharge (m³/s)</td>
                    <td v-for="(_, idx) in monthAbbrList" :key="idx">
                        <span
                            :title = props.monthlyHydrology.monthlyDischarge[idx]
                        >
                            {{ handleDecimalPlaces(+props.monthlyHydrology.monthlyDischarge[idx], 2) }}
                        </span>
                    </td>
                </tr>
                <tr>
                    <td colspan="2">Potential Allocation (m³/s, Risk Mgmt 1)</td>
                    <td v-for="(_, idx) in monthAbbrList" :key="idx">
                        <span
                            :title = props.monthlyHydrology.rm1[idx]
                        >
                            {{ handleDecimalPlaces(+props.monthlyHydrology.rm1[idx], 2) }}
                        </span>
                    </td>
                </tr>
                <tr>
                    <td colspan="2">Potential Allocation (m³/s, Risk Mgmt 2)</td>
                    <td v-for="(_, idx) in monthAbbrList" :key="idx">
                        <span
                            :title = props.monthlyHydrology.rm2[idx]
                        >
                            {{ handleDecimalPlaces(+props.monthlyHydrology.rm2[idx], 2) }}
                        </span>
                    </td>
                </tr>
                <tr>
                    <td colspan="2">Potential Allocation (m³/s, Risk Mgmt 3)</td>
                    <td v-for="(_, idx) in monthAbbrList" :key="idx">
                        <span
                            :title = props.monthlyHydrology.rm3[idx]
                        >
                        {{ props.monthlyHydrology.rm3[idx].slice(0, 1) }} {{ addCommas((+props.monthlyHydrology.rm3[idx].slice(1)).toFixed(2)) }}
                         </span>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<script setup>
import { monthAbbrList } from "@/utils/dateHelpers.js";
import { addCommas, handleDecimalPlaces } from "@/utils/stringHelpers.js";

const props = defineProps({
    monthlyHydrology: {
        type: Object,
        default: () => {},
    },
    isReport: {
        type: Boolean,
        default: false,
    },
});
</script>

<style lang="scss" scoped>
.report-break {
    page-break-before: always;
}

.monthly-hydrology-table {
    width: 100%;

    &.report {
        table {
            td {
                &:first-child {
                    max-width: 7rem;   
                }
            }
        }
    }

    table {
        border-collapse: collapse;
        width: 100%;

        tr {
            &:nth-child(even) {
                background-color: $light-grey-accent;
            }
        }

        td {
            border-top: 1px solid $primary-font-color;
            word-break: break-all;
        }

        td,
        th {
            text-align: end;

            &:first-child {
                text-align: start;
                padding-left: 1em;
            }

            &:last-child {
                padding-right: 1em;
            }
        }
    }
}
</style>
