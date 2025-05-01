<template>
    <q-table
        v-if="!loading && tableRows.length > 0 && tableCols.length > 0"
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
import flowMetrics from '@/constants/flowMetrics.json';
import { onMounted, ref } from 'vue';

const pageProps = {
    stationId: {
        type: Number,
        default: -1,
    }
};

const loading = ref(false);
const tableData = ref();
const tableRows = ref([]);
const tableCols = ref([]);

onMounted(async () => {
    loading.value = true;
    await getFlowMetrics(pageProps.stationId);
    loading.value = false;
});

/**
 * fetches the flow metrics data for the current station
 * @param stationId - the id of the currently selected station
 */
const getFlowMetrics = async (stationId) => {
    // TODO: make API call rather than setting data via fixture json
    // tableData.value = await getFlowMetricsByStationId(stationId)
    tableData.value = flowMetrics;
    formatTableData(tableData.value);
}

const formatTableData = (data) => {
    tableCols.value = data.headers.map(header => {
        return {
            name: header,
            field: header,
            label: header,
        }
    })

    tableRows.value = data.items.map((item) => {
        const someArr = item.map((el, idx) => {
            return {
                [data.headers[idx]]: el
            }
        })

        const mergedList = Object.assign({}, ...someArr);
        return mergedList;
    })
}
</script>
