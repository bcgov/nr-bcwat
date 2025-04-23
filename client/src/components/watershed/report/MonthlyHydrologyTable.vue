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
const props = defineProps({
    monthlyHydrology: {
        type: Object,
        default: () => {},
    },
    monthAbbrList: {
        type: Object,
        default: () => {},
    },
});
</script>

<style lang="scss">
.monthly-hydrology-legend {
    table {
        width: 100%;

        td {
            padding-left: 1em;
            padding-right: 1em;
        }
    }

    .legend-color {
        border: 2px solid black;
        border-radius: 3px;
        height: 1em;
        
        &.existing {
            background-color: $existing-allocations-stroke-color;
        }
        &.rm3 {
            background-color: $risk-mgmt-level-3-color;
        }
        &.rm2 {
            background-color: $risk-mgmt-level-2-color;
        }
        &.rm1 {
            background-color: $risk-mgmt-level-1-color;
        }
    }

    .legend-line {
        display: flex;
        align-items: center;
    
        .line {
            border-width: 2px;
            width: 2.5em;
 
            &.dashed {
                border-style: dashed;

                &.mad {
                    color: $mad-color;
                }
                &.mad20 {
                    color: $mad-20-color;
                }
                &.mad10 {
                    color: $mad-10-color;
                }
            }
        }
    }
}

</style>
