<template>
    <q-table
        v-if="!loading"
        flat
        bordered
        title="Monthly Mean Flow"
        :rows="tableRows"
        :columns="tableCols"
        :pagination="{ rowsPerPage: 0 }"
        separator="cell"
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
                    {{ 
                        props.row[props.cols[idx].name] ? 
                        props.cols[idx].name === 'year' ? props.row[props.cols[idx].name] : 
                        props.row[props.cols[idx].name].toFixed(4) : '-' 
                    }}
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
        type: Object,
        default: () => {},
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
    tableRows.value = props.tableData;

    if('current' in props.tableData){
        const max = [{}];
        const avg = [{}];
        const min = [{}];

        props.tableData.current.forEach(el => {
            max[0][monthAbbrList[el.m - 1]] = el.max;
            avg[0][monthAbbrList[el.m - 1]] = el.avg;
            min[0][monthAbbrList[el.m - 1]] = el.min;
        });

        const groupedByYears = [];
        props.tableData.yearly.forEach(el => {
            const idx = groupedByYears.findIndex(years => years.year === el.year);
            if(idx === -1){
                groupedByYears.push({ year: el.year })
            } else {
                groupedByYears[idx][monthAbbrList[el.m - 1]] = el.v;
            }
        });
        tableRows.value = groupedByYears;
    }
};

/**
 * sets a colour gradient based on the maximum value of the row and the value of the current cell
 *
 * @param row the current table row
 * @param cell the current table cell data
 */
const getColorForRowAndCell = (row, cell) => {
    if(!cell){
        return '#fff';
    }

    const valuesInRow = [];

    // get only the non-string values, anything not '-'
    for (const key in row) {
        if (key !== "year" && typeof row[key] !== "string" && row[key] !== null) {
            valuesInRow.push(row[key]);
        }
    }

    // find the maximum of those values for the row and set the transparency of the background
    const maxVal = Math.max(...valuesInRow);
    const colorGrading = (cell / maxVal) * 99;

    if(valuesInRow.length === 1 && cell !== '-'){
        return cellColor;
    }

    // append the transparency value (out of 99) to the hex code
    return `${cellColor}${100 - Math.floor(colorGrading)}`;
};
</script>

<style lang="scss">
.q-table__container {
    max-height: calc(100vh - 2rem);
    overflow-y: scroll;
}
</style>
