<template>
    <table class="hydrologic-tabular-data">
        <tbody>
            <tr class="month-row">
                <td></td>
                <td>Month</td>
                <td
                    v-for="month in monthAbbrList"
                    :key="month"
                >
                    {{ month }}
                </td>
            </tr>
            <tr class="station-row">
                <td></td>
                <td>Station</td>
                <td
                    v-for="(_, idx) in monthAbbrList"
                    :key="idx"
                >
                    {{ props.tableData.candidates[idx + 1] }}
                </td>
            </tr>
            <tr
                v-for="entry in ['90th', '75th', '50th', '25th', '10th']"
                :key="entry"
                :style="{'background-color': entry === '90th' || entry === '10th' ? props.colorAccent : props.color}"
            >
                <td><span v-if="entry==='90th'">Candidate {{ props.candidate }}</span></td>
                <td>{{ entry }}</td>
                <td
                    v-for="(_, idx) in monthAbbrList"
                    :key="idx"
                >
                    {{ props.tableData[entry][idx + 1].toFixed(2) }}
                </td>
            </tr>
        </tbody>
    </table>
</template>

<script setup>
import { monthAbbrList } from "@/constants/dateHelpers";

const props = defineProps({
    tableData: {
        type: Object,
        default: () => {},
    },
    candidate: {
        type: String,
        default: 0,
    },
    colorAccent: {
        type: String,
        default: '#000',
    },
    color: {
        type: String,
        default: '#000',
    },
});
</script>

<style lang="scss">
.hydrologic-tabular-data {
    border-collapse: collapse;
    color: white;
    margin-bottom: 2em;
    text-align: center;  
    width: 100%;

    .month-row {
        background-color: $color-hydrovar-legend;
    }
    .station-row {
        background-color: $color-hydrovar-legend-accent;
    }
}
</style>
