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
                        <ScientificNotation
                            :num="+props.monthlyHydrology.waterLicenceMonthlyDisplay[idx]"
                        />
                    </q-td>
                </q-tr>
                <q-tr>
                    <q-td>
                        Existing Short Term Approvals*
                        <div>(m³/s)</div>
                    </q-td>
                    <q-td v-for="(_, idx) in monthAbbrList" :key="idx">
                        <ScientificNotation
                            :num="+props.monthlyHydrology.shortTermAllocationMonthlyDisplay[idx]"
                        />
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
                        <ScientificNotation
                            :num="+props.monthlyHydrology.monthlyDischarge[idx]"
                        />
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
                        <ScientificNotation
                            :num="+props.monthlyHydrology.rm1[idx]"
                        />
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
                            <ScientificNotation
                                :num="+props.monthlyHydrology.rm2[idx]"
                            />
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
                            {{ props.monthlyHydrology.rm3[idx].slice(0, 1) }}&nbsp;
                        </span>
                        <ScientificNotation
                            :num="+props.monthlyHydrology.rm3[idx].slice(1)"
                        />
                    </td>
                </q-tr>
            </template>
        </q-table>
    </div>
</template>

<script setup>
import { monthAbbrList } from "@/utils/dateHelpers";
import ScientificNotation from "@/components/ScientificNotation.vue";

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
