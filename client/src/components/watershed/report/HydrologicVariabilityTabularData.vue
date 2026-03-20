<template>
    <table 
        v-if="!props.isReport"
        class="hydrologic-tabular-data"
    >
        <tbody>
            <tr class="month-row">
                <td></td>
                <td>Month</td>
                <td v-for="month in monthAbbrList" :key="month">
                    {{ month }}
                </td>
            </tr>
            <tr class="station-row">
                <td></td>
                <td>Station</td>
                <td v-for="(_, idx) in monthAbbrList" :key="idx">
                    {{ props.tableData.candidates[idx + 1] }}
                </td>
            </tr>
            <tr
                v-for="entry in ['90th', '75th', '50th', '25th', '10th']"
                :key="entry"
                :style="{
                    'background-color':
                        entry === '90th' || entry === '10th'
                            ? props.colorAccent
                            : props.color,
                }"
            >
                <td>
                    <span v-if="entry === '90th'"
                        >Candidate {{ props.candidate }}</span
                    >
                </td>
                <td>{{ entry.replace("50th", "Mean") }}</td>
                <td v-for="(_, idx) in monthAbbrList" :key="idx">
                    {{ addCommas(props.tableData[entry][idx + 1].toFixed(2)) }}
                </td>
            </tr>
        </tbody>
    </table>
    <table 
        v-else
        class="hydrologic-tabular-data report"
    >
        <tbody>
            <tr 
                class="month-row"
                :style="{
                    'background-color': props.colorAccent
                }"
            >
                <td>Month</td>
                <td 
                    v-for="month in monthAbbrList" :key="month"
                >
                    {{ month }}
                </td>
            </tr>
            <tr
                v-for="entry in ['90th', '75th', '50th', '25th', '10th']"
                :key="entry"
                :style="getRowStyle(entry)"
            >
                <td>{{ entry.replace("50th", "Mean") }}</td>
                <td v-for="(_, idx) in monthAbbrList" :key="idx">
                    {{ addCommas(props.tableData[entry][idx + 1].toFixed(2)) }}
                </td>
            </tr>
        </tbody>
    </table>
</template>

<script setup>
import { monthAbbrList } from "@/utils/dateHelpers";
import { addCommas } from "@/utils/stringHelpers";

const props = defineProps({
    tableData: {
        type: Object,
        default: () => {},
    },
    candidate: {
        type: Number,
        default: 0,
    },
    colorAccent: {
        type: String,
        default: "#000",
    },
    color: {
        type: String,
        default: "#000",
    },
    isReport: {
        type: Boolean,
        default: false,
    }
});

const getRowStyle = (entry) => {
    if(entry === "50th"){
        return { 'background-color': "#aaa", "color": "#333"};
    }
    if (entry === "90th" || entry === "10th") {
        return { 'background-color': props.colorAccent };
    }
    return { 'background-color': props.color };
}
</script>

<style lang="scss">
.hydrologic-tabular-data {
    border-collapse: collapse;
    color: white;
    margin-bottom: 2em;
    font-size: 10px;
    text-align: center;
    width: 100%;

    &.report {
        border-collapse: separate;
    }

    .month-row {
        background-color: $color-hydrovar-legend;
    }

    .station-row {
        background-color: $color-hydrovar-legend-accent;
    }
}
</style>
