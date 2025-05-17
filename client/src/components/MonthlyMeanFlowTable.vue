<template>
    <q-table
        v-if="!loading"
        flat
        bordered
        title="Monthly Mean Flow"
        :rows="tableRows"
        :columns="tableCols"
        :pagination="{ rowsPerPage: 0 }"
        hide-pagination
    >
        <template #body="props">
            <q-tr :props="props">
                <q-td
                    v-for="(_, idx) in tableCols"
                    key="year"
                    :props="props"
                    :style="
                        idx !== 0
                            ? `background-color: ${getColorForRowAndCell(
                                  props.row,
                                  props.row[Object.keys(props.row)[idx]]
                              )}`
                            : ''
                    "
                >
                    {{ props.row[Object.keys(props.row)[idx]] }}
                </q-td>
            </q-tr>
        </template>
    </q-table>
    <div v-else>
        <q-skeleton />
    </div>
</template>

<script setup>
import { monthAbbrList } from "@/utils/dateHelpers.js";
import { onMounted, ref } from "vue";

const loading = ref(false);
const tableCols = ref([]);
const tableRows = ref([]);
const cellColor = "#6f91a4";

const props = defineProps({
    tableData: {
        type: Array,
        default: () => [],
    }
});

onMounted(async () => {
    loading.value = true;
    setTableData();
    loading.value = false;
});

/**
 * formats the raw data into a format digestible by the table layout
 */
const setTableData = () => {
    // set the columns
    tableCols.value = [{ name: "year", label: "Year", field: "year" }];
    monthAbbrList.forEach((month) => {
        tableCols.value.push({
            name: month,
            label: month,
            field: month,
        });
    });

    // set the rows
    tableRows.value = [];

    const foundVars = [
        { name: "Mean", type: "avg", found: false },
        { name: "Maximum", type: "max", found: false },
        { name: "Minimum", type: "min", found: false },
    ];
    // populate rows with mean, max, min data
    props.tableData.value.monthly_mean_flow.current.forEach((el) => {
        foundVars.forEach((type) => {
            type.found = tableRows.value.find((row) => row.year === type.name);
            if (!type.found) {
                tableRows.value.push({
                    year: type.name,
                    [monthAbbrList[el.m - 1]]: el[type.type]
                        ? el[type.type]
                        : "-",
                });
            } else {
                type.found[monthAbbrList[el.m - 1]] = el[type.type]
                    ? el[type.type]
                    : "-";
            }
        });
    });

    // populate rows with yearly data
    props.tableData.value.monthly_mean_flow.yearly.forEach((el) => {
        const foundRow = tableRows.value.find((row) => row.year === el.year);
        if (!foundRow) {
            tableRows.value.push({
                year: el.year,
                [monthAbbrList[el.m - 1]]: el.v ? el.v : "-",
            });
        } else {
            foundRow[monthAbbrList[el.m - 1]] = el.v ? el.v : "-";
        }
    });
};

/**
 * sets a colour gradient based on the maximum value of the row and the value of the current cell
 *
 * @param row the current table row
 * @param cell the current table cell data
 */
const getColorForRowAndCell = (row, cell) => {
    const valuesInRow = [];

    // get only the non-string values, anything not '-'
    for (const key in row) {
        if (key !== "year" && typeof row[key] !== "string") {
            valuesInRow.push(row[key]);
        }
    }

    // find the maximum of those values for the row and set the transparency of the background
    const maxVal = Math.max(...valuesInRow);
    const colorGrading = (cell / maxVal) * 99;

    // append the transparency value (out of 99) to the hex code
    return `${cellColor}${100 - Math.floor(colorGrading)}`;
};
</script>
