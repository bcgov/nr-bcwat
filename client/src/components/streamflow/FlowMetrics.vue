<template>
    <q-table
        v-if="tableRows.length > 0 && tableCols.length > 0"
        title="Flow Metrics"
        :columns="tableCols"
        :rows="tableRows"
        flat bordered
        :pagination="{ rowsPerPage: 0 }"
        separator="cell"
        hide-pagination
        data-cy="flow-metrics-table"
    >
    </q-table>
</template>

<script setup>
import { onMounted, ref } from 'vue';

const props = defineProps({
    tableData: {
        type: Object,
        default: () => {},
    }
});

const loading = ref(false);
const tableRows = ref([]);
const tableCols = ref([]);

onMounted(async () => {
    loading.value = true;
    formatTableData(props.tableData);
    loading.value = false;
});

const formatTableData = (data) => {
    if(data.length > 0){
        tableCols.value = [
            { name: 'Parameter', field: 'Parameter', label: 'Parameter' },
            { name: '200', field: '200', label: '200' },
            { name: '100', field: '100', label: '100' },
            { name: '50', field: '50', label: '50' },
            { name: '25', field: '25', label: '25' },
            { name: '20', field: '20', label: '20' },
            { name: '10', field: '10', label: '10' },
            { name: '5', field: '5', label: '5' },
            { name: '2', field: '2', label: '2' },
            { name: '1.01', field: '1.01', label: '1.01' },
            { name: '1', field: '1', label: '1' },
            { name: 'Years of data', field: 'Years of data', label: 'Years of data' },
        ];
        tableRows.value = data;
    }
};
</script>
