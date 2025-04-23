<template>
    <div class="monthly-hydrology-table">
        <table>
            <tbody>
                <tr>
                    <th></th>
                    <th
                        v-for="month in monthAbbrList"
                        :key="month"
                    >
                        {{ month }}
                    </th>
                </tr>
                <tr>
                    <td>% of MAD</td>
                    <td
                        v-for="(_, idx) in monthAbbrList"
                        :key="idx"
                    >
                        {{ props.monthlyHydrology.monthlyDischargePercentages[idx] }}
                    </td>
                </tr>
                <tr>
                    <td>Flow Sensitivity</td>
                    <td
                        v-for="(_, idx) in monthAbbrList"
                        :key="idx"
                    >
                        {{ props.monthlyHydrology.monthlyFlowSensitivies[idx] }}
                    </td>
                </tr>
                <tr>
                    <td>Existing Water Licences* (m³/s))</td>
                    <td
                        v-for="(_, idx) in monthAbbrList"
                        :key="idx"
                    >
                        {{ props.monthlyHydrology.existingAllocations[idx] }}
                    </td>
                </tr>
                <tr>
                    <td>Existing Short Term Approvals* (m³/s)</td>
                    <td
                        v-for="(_, idx) in monthAbbrList"
                        :key="idx"
                    >
                        {{ props.monthlyHydrology.shortTermAllocationMonthlyDisplay[idx] }}
                    </td>
                </tr>
                <tr>
                    <td>Mean Monthly Discharge (m³/s)</td>
                    <td
                        v-for="(_, idx) in monthAbbrList"
                        :key="idx"
                    >
                        {{ props.monthlyHydrology.monthlyDischarge[idx] }}
                    </td>
                </tr>
                <tr>
                    <td>Potential Allocation (m³/s, Risk Mgmt 1)</td>
                    <td
                        v-for="(_, idx) in monthAbbrList"
                        :key="idx"
                    >
                        {{ props.monthlyHydrology.rm1[idx] }}
                    </td>
                </tr>
                <tr>
                    <td>Potential Allocation (m³/s, Risk Mgmt 2)</td>
                    <td
                        v-for="(_, idx) in monthAbbrList"
                        :key="idx"
                    >
                        {{ props.monthlyHydrology.rm2[idx] }}
                    </td>
                </tr>
                <tr>
                    <td>Potential Allocation (m³/s, Risk Mgmt 3)</td>
                    <td
                        v-for="(_, idx) in monthAbbrList"
                        :key="idx"
                    >
                        {{ props.monthlyHydrology.rm3[idx] }}
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<script setup>
import { monthAbbrList } from "@/constants/dateHelpers";

const props = defineProps({
    monthlyHydrology: {
        type: Object,
        default: () => {},
    },
});
</script>

<style lang="scss">
.monthly-hydrology-table {
    width: 100%;
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
        }

        td, th {
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
