<template>
    <div v-if="tableData">
        <q-table
            v-if="!loading"
            flat
            bordered
            title="Monthly Mean Levels (depth to water, m)"
            :rows="tableRows"
            :columns="tableCols"
            :pagination="{ rowsPerPage: 0 }"
            separator="cell"
            hide-pagination
        >
            <template #body="props">
                <q-tr :props="props">
                    <q-td
                        v-for="(col, idx) in tableCols"
                        key="year"
                        :props="props"
                        :style="
                            col.name !== 'year' ?
                            `background-color: ${getColorForRowAndCell(
                                props.row,
                                col.name
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
    </div>
    <div 
        v-else
        class="no-data"
    >
        <q-card class="q-pa-sm text-center">
            <div>No Data Available</div>
        </q-card>
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
const getColorForRowAndCell = (row, column) => {
    const valuesInRow = [];

    // get only the non-string values, anything not '-'
    Object.keys(row).forEach(el => {
        if (el !== "year") {
            valuesInRow.push(row[el]);
        }
    })

    const maximum = Math.max(...valuesInRow)
    const ratio = (row[column] / maximum) * 99;   

    return `${cellColor}${ratio.toFixed(0)}`
};
</script>

<style lang="scss">
.q-table__container {
    max-height: calc(100vh - 2rem);
    overflow-y: scroll;
}
</style>
