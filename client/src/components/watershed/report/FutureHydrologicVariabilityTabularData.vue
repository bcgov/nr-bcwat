<template>
    <table class="hydrologic-tabular-data">
        <tbody>
            <tr class="month-row">
                <td></td>
                <td>Month</td>
                <td v-for="month in monthAbbrList" :key="month">
                    {{ month }}
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
                        >{{ props.year }} - {{ endYear }}</span
                    >
                </td>
                <td>{{ entry.replace("50th", "Mean") }}</td>
                <td v-for="(_, idx) in monthAbbrList" :key="idx">
                    {{ props.tableData[entry][idx + 1].toFixed(2) }}
                </td>
            </tr>
        </tbody>
    </table>
</template>

<script setup>
import { monthAbbrList } from "@/utils/dateHelpers";
import { computed } from 'vue';


const props = defineProps({
    tableData: {
        type: Object,
        default: () => {},
    },
    year: {
        type: String,
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

});


const endYear = computed(() => {
    if (props.year === "1976") {
        return "2006";
    } else if (props.year === "2011") {
        return "2040";
    } else if (props.year === "2041") {
        return "2070";
    } else if (props.year === "2071") {
        return "2100";
    }
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
