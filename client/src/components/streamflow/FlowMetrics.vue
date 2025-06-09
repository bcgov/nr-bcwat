<template>
    {{ tableRows }}
    <!-- <q-table
        v-if="tableRows.length > 0 && tableCols.length > 0"
        title="Flow Metrics"
        :columns="tableCols"
        :rows="tableRows"
        flat bordered
        :pagination="{ rowsPerPage: 0 }"
        separator="cell"
        hide-pagination
    >
    </q-table> -->
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
    tableCols.value = data.headers.map((colNameString) => {
        return {
            name: colNameString, 
            label: colNameString,
            align: 'center',
        }
    });

    data.items.forEach((item, itemIdx) => {

        const ah = tableCols.value.map((colKey, idx) => {
            return {
                [colKey.name]: item[idx]
            }
        })

        console.log(ah)
    })
};
</script>
