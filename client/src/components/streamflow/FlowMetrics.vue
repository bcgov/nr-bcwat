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
            { name: 'Parameter' },
        ]

        tableRows.value = data;
    }

    console.log(tableCols.value)
};
</script>
