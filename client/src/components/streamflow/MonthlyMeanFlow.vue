<template>
    <h3>Monthly Mean Flow</h3>
    <div>
        {{ monthlyMeanFlow.monthly_mean_flow }}
    </div>
    <q-table
        v-if="tableCols.length > 0 && tableRows.length > 0 && !loading"
        flat bordered
        title="Treats"
        dense
        :rows="tableRows"
        :columns="tableCols"
        row-key="name"
    />
</template>

<script setup>
import monthlyMeanFlow from '@/constants/monthlyMeanFlow.json';
import { monthAbbrList } from '@/constants/dateHelpers.js';
import { onMounted, ref } from 'vue';

const loading = ref(false);
const tableData = ref();
const tableCols = ref([])

onMounted(async () => {
    loading.value = true;
    await getTableData();
    setTableData();
    loading.value = false;
})

const setTableData = () => {
    // set the columns
    tableCols.value = monthAbbrList.map((month, idx) => {
        return {
            name: idx + 1,
            label: month,
            field: idx + 1,
        }
    })

    tableData.value.monthly_mean_flow.current.map((el, idx) => {
        return {
            name: 
        }
    })
}

const getTableData = () => {
    // TODO add API fetch call here for the monthly mean flow data
    tableData.value = monthlyMeanFlow;
}


</script>
