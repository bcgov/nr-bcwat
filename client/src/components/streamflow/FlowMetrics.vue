<template>
    <h3>Flow Metrics</h3>
    <q-table
        v-if="!loading"
        :columns="tableCols"
        :rows="tableRows"
        flat bordered
        :pagination="{ rowsPerPage: 0 }"
        hide-pagination
    >
        <template #body="props">
            <q-tr :props="props">
                <q-td :props="props">
                    test
                </q-td>
            </q-tr>
        </template>
    </q-table>
</template>

<script setup>
import flowMetrics from '@/constants/flowMetrics.json';
import { onMounted, ref } from 'vue';

const props = {
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
    await getFlowMetrics(props.stationId);
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
            label: header
        }
    })

    tableRows.value = data.items.map((item) => {
        return item.map((el, idx) => {
            return {
                [data.headers[idx]]: el
            }
        })
    })
}
</script>
