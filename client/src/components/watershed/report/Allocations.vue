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
            dense
            flat
            wrap-cells
        >
            <template #body="props">
                <q-tr :props="props">
                    <td class="wow" style="word-wrap: break-word">
                        <p>{{ props.row.licensee }}</p>
                        <p>
                            {{ props.row.purpose }} from
                            {{ props.row.stream_name }} ({{
                                props.row.sourcetype
                            }})
                        </p>
                    </td>
                    <td>
                        <p>{{ props.row.licence_no }}</p>
                        <p v-if="props.row.file_no">
                            File # {{ props.row.file_no }}
                        </p>
                    </td>
                    <td>
                        <p>{{ props.row.pod }}</p>
                        <p v-if="props.row.well_tag_number">
                            WTN: {{ props.row.well_tag_number }}
                        </p>
                    </td>
                    <td>
                        <p v-if="props.row.start_date">
                            Start:
                            {{
                                new Date(
                                    props.row.start_date
                                ).toLocaleDateString(undefined, {
                                    month: "short",
                                    year: "numeric",
                                    day: "2-digit",
                                })
                            }}
                        </p>
                        <p v-if="props.row.priority_date">
                            Priority:
                            {{
                                new Date(
                                    props.row.priority_date
                                ).toLocaleDateString(undefined, {
                                    month: "short",
                                    year: "numeric",
                                    day: "2-digit",
                                })
                            }}
                        </p>
                        <p v-if="props.row.expiry_date">
                            Exp:
                            {{
                                new Date(
                                    props.row.expiry_date
                                ).toLocaleDateString(undefined, {
                                    month: "short",
                                    year: "numeric",
                                    day: "2-digit",
                                })
                            }}
                        </p>
                        <p v-if="props.row.lic_status_date">
                            Status:
                            {{
                                new Date(
                                    props.row.lic_status_date
                                ).toLocaleDateString(undefined, {
                                    month: "short",
                                    year: "numeric",
                                    day: "2-digit",
                                })
                            }}
                        </p>
                    </td>
                    <td>
                        {{ props.row.qty_display }}
                    </td>
                    <td>
                        {{ props.row.qty_flag }}
                    </td>
                    <td>
                        {{ props.row.lic_type }}
                    </td>
                    <td>
                        {{ props.row.lic_status }}
                    </td>
                </q-tr>
                <!-- <q-tr v-if="props.row.file_no">
                    <td colspan="8">
                        {{ props.row.documentation }}
                    </td>
                </q-tr> -->
            </template>
        </q-table>
        <!-- <pre>{{ filteredAllocations }}</pre> -->
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

const filteredAllocations = computed(() => {
    return props.reportContent.allocations;
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
        align: "center",
        sortable: true,
    },
];
</script>

<style lang="scss" scoped>
td {
    &:first-child {
        max-width: 15vw;
    }
    p {
        margin-bottom: 0px !important;
    }
}
</style>
