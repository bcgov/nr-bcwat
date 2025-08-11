<template>
    <div v-if="tableRows.length > 0 && tableCols.length > 0">
        <p>
            The BC Streamflow Inventory describes hydrologic characteristics at long-term hydrometric monitoring stations in the province.
            Originally produced by C.H. Coulson and W. Obedkoff in 1998, these calculations have recently been updated by A. Ahmed to represent the more recent normal of 1981-2010.
            Calculations are based on data published in the HYDAT archive by the Water Survey of Canada.
            For more information, the reports are available from Ecocat by searching "Inventory of Streamflow" at <a href="http://a100.gov.bc.ca/pub/acat/public/welcome.do" target="_blank">http://a100.gov.bc.ca/pub/acat/public/welcome.do</a>
        </p>
        <q-table
            title="Flow Metrics"
            :columns="tableCols"
            :rows="tableRows"
            flat bordered
            :pagination="{ rowsPerPage: 0 }"
            separator="cell"
            hide-pagination
            data-cy="flow-metrics-table"
        >
            <template #header="tableProps">
                <q-tr class="no-borders">
                    <q-th></q-th>
                    <q-th colspan="10">Return Period (Years)</q-th>
                    <q-th></q-th>
                </q-tr>
                <q-tr>
                    <q-th
                        v-for="column in tableProps.cols.filter(el => el.label !== 'Date')"
                        :key="column.name"
                        :props="tableProps"
                    >
                        {{ column.label }}
                    </q-th>
                </q-tr>
            </template>
        </q-table>
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

<style lang="scss">
.no-borders {
    th {
        border-left: none;
        border-right: none;
    }
}
</style>
