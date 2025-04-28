<template>
    <div>
        <h1 class="q-mb-lg">Allocations</h1>
        <p>
            Water licences and short term use approvals, (collectively,
            ‘allocations’) for surface water and groundwater in British Columbia
            are managed under the Water Sustainability Act. These allocations
            are authorized by the Ministry of Forests, and the BC Energy
            Regulator (associated with activities regulated under the Oil and
            Gas Activities Act). Existing allocations, and active water licence
            applications within the query basin are summarized and listed in the
            charts and tables below.
        </p>
        <q-table
            :rows="filteredAllocations"
            :columns="columns"
            row-key="name"
            title="BC Water Sustainability Act - Water Licences - 2 Licences, 8,800 m³ Total Annual Volume"
            flat
            :hide-pagination="true"
            :pagination="pagination"
        >
        </q-table>
        <!-- <pre>{{ filteredAllocations[0] }}</pre> -->
        <hr />
    </div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
    reportContent: {
        type: Object,
        default: () => {},
    },
});

const pagination = { rowsPerPage: 0 };

const filteredAllocations = computed(() => {
    return props.reportContent.allocations;
    const myAllocations = [];

    props.reportContent.allocations.forEach((allocation) => {
        myAllocations.push({
            licence: allocation.licensee,
            number: allocation.licence_no,
            file_no: allocation.file_no,
            pod: allocation.pod,
            date: allocation.start_date,
            expiry_date: allocation.expiry_date,
            lic_status_date: allocation.lic_status_date,
            priority_date: allocation.priority_date,
            quantity: allocation.qty_display,
            flag: allocation.qty_flag,
            type: allocation,
            status: allocation,
        });
    });

    return myAllocations;
});

const columns = [
    {
        name: "licene",
        field: "licensee",
        label: "Licence",
        align: "left",
        sortable: true,
    },
    {
        name: "number",
        field: "licence_no",
        label: "Number",
        align: "left",
        sortable: true,
    },
    {
        name: "pod",
        field: "pod",
        label: "POD",
        align: "left",
        sortable: true,
    },
    {
        name: "date",
        field: "date",
        label: "Date",
        align: "left",
        sortable: true,
    },
    {
        name: "quantity",
        field: "qty_display",
        label: "Quantity",
        align: "left",
        sortable: true,
    },
    {
        name: "flag",
        field: "qty_flag",
        label: "Flag",
        align: "right",
        sortable: true,
    },
    {
        name: "type",
        field: "lic_type",
        label: "Type",
        align: "left",
        sortable: true,
    },
    {
        name: "status",
        field: "lic_status",
        label: "Status",
        align: "right",
        sortable: true,
    },
];
</script>
