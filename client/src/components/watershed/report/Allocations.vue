<template>
    <div v-if="props.reportContent?.allocations">
        <div class="allocations-container">
            <div :class="props.isReport ? 'report-section-header' : ''">
                <div class="text-h4 q-my-lg">Allocations</div>
            </div>
            <p>
                Water licences<NoteLink :note-number="8" /> and short term use
                approvals<NoteLink :note-number="10" /><sup>,</sup
                ><NoteLink :note-number="8" /> (collectively, ‘allocations’) for surface
                water and groundwater in British Columbia are managed under the Water
                Sustainability Act<NoteLink :note-number="10" />. These allocations are
                authorized by the Ministry of Forests, and the BC Energy Regulator
                (associated with activities regulated under the Oil and Gas Activities
                Act<NoteLink :note-number="11" />). Existing allocations, and active
                water licence applications<NoteLink :note-number="9" />
                within the query basin are summarized and listed in the charts and
                tables below.
            </p>

            <div v-if="props.isReport" class="footer">
                <div v-if="props.reportContent?.overview?.lic_count > 500">
                    The table below has been limited to show the top 500 results based on
                    largest water volumes
                </div>
                <div v-if="props.reportContent?.overview?.lic_count === 0" class="text-h5 q-my-lg">
                    No Allocations for selected watershed.
                </div>
            </div>

            <div v-if="props.isReport">
                <div
                    v-if="props.reportContent.overview.lic_count > 0"
                    class="full-list"
                >
                    <div v-for="table in fullListTables" class="report-break">
                        <div v-if="table.data.length > 0">
                            <div class="report-header" :class="table.class">
                                <div class="text-h5 q-my-lg">{{ table.title }}</div>
                            </div>
                            <q-table
                                class="allocations-report-table"
                                :rows="
                                table.data
                                    .slice(0, 500)
                                    .sort((a, b) => a.display_ann_qty - b.display_ann_qty)
                                "
                                :columns="baseColumns"
                                row-key="name"
                                dense
                                flat
                                wrap-cells
                                hide-pagination
                                :pagination="{ rowsPerPage: 0 }"
                            >
                                <template #top>
                                    <div class="allocations-table-top">
                                        <div class="text-h6">{{ table.type }}</div>
                                        <p>{{ table.description }}</p>

                                        <div v-if="table.data.length > 500" class="q-pa-md">
                                            <p>
                                                The table below has been limited to show the top 500
                                                results based on largest water volumes
                                            </p>
                                        </div>
                                    </div>
                                </template>
                                <template #body="bodyProps">
                                    <q-tr :props="bodyProps">
                                        <td>
                                            <p>{{ bodyProps.row.licensee }}</p>
                                            <p>
                                                {{ bodyProps.row.purpose }} from
                                                {{ bodyProps.row.stream_name }} ({{
                                                bodyProps.row.sourcetype
                                                }})
                                            </p>
                                        </td>
                                        <td>
                                            <p>{{ bodyProps.row.licence_no }}</p>
                                            <p v-if="bodyProps.row.file_no">
                                                File # {{ bodyProps.row.file_no }}
                                            </p>
                                        </td>
                                        <td>
                                            <p>{{ bodyProps.row.pod }}</p>
                                            <p v-if="bodyProps.row.well_tag_number">
                                                WTN: {{ bodyProps.row.well_tag_number }}
                                            </p>
                                        </td>
                                        <td>
                                            <p v-if="bodyProps.row.start_date">
                                                Start:
                                                {{
                                                    dayjs(new Date(bodyProps.row.start_date)).format(
                                                        "ddd MMM YYYY",
                                                    )
                                                }}
                                            </p>
                                            <p v-if="bodyProps.row.priority_date">
                                                Priority:
                                                {{
                                                    dayjs(new Date(bodyProps.row.priority_date)).format(
                                                        "ddd MMM YYYY",
                                                    )
                                                }}
                                            </p>
                                            <p v-if="bodyProps.row.expiry_date">
                                                Exp:
                                                {{
                                                    dayjs(new Date(bodyProps.row.expiry_date)).format(
                                                        "ddd MMM YYYY",
                                                    )   
                                                }}
                                            </p>
                                            <p v-if="bodyProps.row.lic_status_date">
                                                Status:
                                                {{
                                                    dayjs(new Date(bodyProps.row.lic_status_date)).format(
                                                        "ddd MMM YYYY",
                                                    )
                                                }}
                                            </p>
                                        </td>
                                        <td>
                                            {{ addCommas((+bodyProps.row.display_ann_qty || 0).toFixed(1)) }}
                                        </td>
                                        <td>
                                            {{ bodyProps.row.qty_flag }}
                                        </td>
                                    </q-tr>
                                </template>
                            </q-table>
                        </div>
                    </div>
                </div>
            </div>
            <div v-else>
                <q-table
                    v-if="props.reportContent?.overview?.lic_count > 0"
                    :rows="filteredAllocations"
                    :columns="columns"
                    row-key="name"
                    dense
                    flat
                    wrap-cells
                >
                    <template #top>
                        <div class="text-h5 primary-font-text">
                            BC Water Sustainability Act - Water Licences -
                            {{ addCommas(props.reportContent.overview.lic_count) }} Licences,
                            {{
                                addCommas(
                                (+props.reportContent.annualHydrology.allocs_m3yr
                                    .query || 0).toFixed(1),
                                )
                            }}
                            m³ Total Annual Volume<NoteLink :note-number="9" />
                        </div>
                        <q-btn icon="mdi-filter" flat class="primary-font-text">
                        <q-menu class="allocations-filter-menu q-pa-md">
                            <div 
                                v-for="type in tableFilters"
                            >
                                <div class="text-h6">{{ type.label }}</div>
                                <div class="side-by-side">
                                    <q-checkbox v-for="option in type.options" :label="option.label" v-model="filters[option.model][option.value]" />
                                </div>
                            </div>
                            <q-input
                                v-model="filters.text"
                                class="q-mb-sm"
                                dense
                                placeholder="Text Search"
                            />
                            <q-btn
                                label="Reset Filters"
                                dense
                                outlined
                                color="primary"
                                @click="resetFilters()"
                            />
                        </q-menu>
                        </q-btn>
                    </template>
                    <template #body="bodyProps">
                        <q-tr :props="bodyProps">
                            <td data-cy="license">
                                <p>{{ bodyProps.row.licensee }}</p>
                                <p>
                                    {{ bodyProps.row.purpose }} from
                                    {{ bodyProps.row.stream_name }} ({{
                                        bodyProps.row.sourcetype
                                    }})
                                </p>
                            </td>
                            <td data-cy="number">
                                <p>{{ bodyProps.row.licence_no }}</p>
                                <p v-if="bodyProps.row.file_no">
                                    File # {{ bodyProps.row.file_no }}
                                </p>
                            </td>
                            <td data-cy="pod">
                                <p>{{ bodyProps.row.pod }}</p>
                                <p v-if="bodyProps.row.well_tag_number">
                                    WTN: {{ bodyProps.row.well_tag_number }}
                                </p>
                            </td>
                            <td data-cy="date">
                                <p v-if="bodyProps.row.start_date">
                                    Start:
                                    {{
                                        dayjs(new Date(bodyProps.row.start_date)).format(
                                        "ddd MMM YYYY",
                                        )
                                    }}
                                </p>
                                <p v-if="bodyProps.row.priority_date">
                                    Priority:
                                    {{
                                        dayjs(new Date(bodyProps.row.priority_date)).format(
                                        "ddd MMM YYYY",
                                        )
                                    }}
                                </p>
                                <p v-if="bodyProps.row.expiry_date">
                                    Exp:
                                    {{
                                        dayjs(new Date(bodyProps.row.expiry_date)).format(
                                        "ddd MMM YYYY",
                                        )
                                    }}
                                </p>
                                <p v-if="bodyProps.row.lic_status_date">
                                    Status:
                                    {{
                                        dayjs(new Date(bodyProps.row.lic_status_date)).format(
                                        "ddd MMM YYYY",
                                        )
                                    }}
                                </p>
                            </td>
                            <td data-cy="quantity">
                                {{ addCommas((+bodyProps.row.display_ann_qty || 0).toFixed(1)) }}
                            </td>
                            <td data-cy="flag">
                                {{ bodyProps.row.qty_flag }}
                            </td>
                            <td data-cy="type">
                                <div class="licence-box" :class="bodyProps.row.lic_type">
                                    {{ bodyProps.row.lic_type }}
                                </div>
                            </td>
                            <td data-cy="status">
                                <q-icon
                                    v-if="bodyProps.row.lic_status === 'CURRENT'"
                                    name="mdi-check-circle"
                                    size="sm"
                                    color="green-5"
                                />
                            </td>
                        </q-tr>
                    </template>
                </q-table>
                <div v-if="props.reportContent?.overview?.lic_count === 0" class="text-h5 q-my-lg">
                    No Allocations for selected watershed.
                </div>
            </div>
            <div>
                To get more information about a specific licence, please search the
                licence number at this
                <a
                href="https://j200.gov.bc.ca/pub/ams/Default.aspx?PossePresentation=AMSPublic&PosseMenuName=WS_Main&PosseObjectDef=o_ATIS_DocumentSearch"
                target="_blank"
                >site</a>
            </div>
        </div>
        <q-separator class="q-my-xl" />
    </div>
</template>

<script setup>
import NoteLink from "@/components/watershed/report/NoteLink.vue";
import dayjs from "dayjs";
import { computed, onMounted, ref } from "vue";
import { addCommas } from "@/utils/stringHelpers";

const props = defineProps({
    reportContent: {
        type: Object,
        default: () => {},
    },
    isReport: {
        type: Boolean,
        default: false,
    },
});

onMounted(async () => {
    document.allocationsLoaded = true;
});

const filters = ref({
    source: {
        sw: true,
        gw: true,
    },
    term: {
        long: true,
        short: true,
        app: true,
    },
    purpose: {
        agriculture: true,
        commercial: true,
        domestic: true,
        municipal: true,
        power: true,
        oilgas: true,
        storage: true,
        other: true,
    },
    text: "",
});

const filteredAllocations = computed(() => {
    const myAllocations = [];

    props.reportContent.allocations.forEach((allocation) => {
        if (!filters.value.source.sw && allocation.water_allocation_type === "SW") return;
        if (!filters.value.source.gw && allocation.water_allocation_type === "GW") return;
        if (!filters.value.term.long && allocation.licence_term === "long") return;
        if (!filters.value.term.short && allocation.licence_term === "short") return;
        if (!filters.value.term.app && allocation.licence_term === "application") return;
        if (!filters.value.purpose.agriculture && allocation.purpose_groups === "Agriculture") return;
        if (!filters.value.purpose.commercial && allocation.purpose_groups === "Commercial") return;
        if (!filters.value.purpose.domestic && allocation.purpose_groups === "Domestic") return;
        if (!filters.value.purpose.municipal && allocation.purpose_groups === "Municipal") return;
        if (!filters.value.purpose.power && allocation.purpose_groups === "Power") return;
        if (!filters.value.purpose.oilgas && allocation.purpose_groups === "Oil & Gas") return;
        if (!filters.value.purpose.storage && allocation.purpose_groups === "Storage") return;
        if (!filters.value.purpose.other && allocation.purpose_groups === "Other") return;
        if (filters.value.text.length > 0) {
            if (
                !allocation.licensee.includes(filters.value.text) && 
                !allocation.licence_no.includes(filters.value.text) && 
                !allocation.file_no.includes(filters.value.text) && 
                !allocation.pod.includes(filters.value.text) && 
                !(allocation.well_tag_number !== null ? `${allocation.well_tag_number}`.includes(filters.value.text) : false)
            ) {
                return;
            }
        }
        myAllocations.push(allocation);
    });
    return myAllocations;
});

const fullListTables = computed(() => {
    const tables = [];

    const groundwaterLicences = [];
    const surfacewaterLicences = [];
    const groundwaterApplications = [];
    const surfacewaterApplications = [];

    filteredAllocations.value.forEach((allocation) => {
        if (allocation.water_allocation_type === "GW") {
            groundwaterLicences.push(allocation);
            if (allocation.lic_status === "ACTIVE APPL.") {
                groundwaterApplications.push(allocation);
            }
        }
        if (allocation.water_allocation_type === "SW") {
            surfacewaterLicences.push(allocation);
            if (allocation.lic_status === "ACTIVE APPL.") {
                surfacewaterApplications.push(allocation);
            }
        }
    });

    if (surfacewaterLicences.length) {
        tables.push({
            title: "Water Licences (Surface Water)",
            data: surfacewaterLicences,
            type: "Existing Allocations",
            description: "Current approved surface water licences",
            class: "surface-water-licence",
        });
    }
    if (groundwaterLicences.length) {
        tables.push({
            title: "Water Licences (Groundwater)",
            data: groundwaterLicences,
            type: "Existing Allocations",
            description: "Current approved groundwater licences",
            class: "groundwater-licence",
        });
    }
    if (surfacewaterApplications.length) {
        tables.push({
            title: "Water Licence Applications (Surface Water)",
            data: surfacewaterApplications,
            type: "Active Applications",
            description: "Active applications for surface water licences",
            class: "surface-water-application",
        });
    }
    if (groundwaterApplications.length) {
        tables.push({
            title: "Water Licence Applications (Groundwater)",
            data: groundwaterApplications,
            type: "Active Applications",
            description: "Active applications for groundwater licences",
            class: "groundwater-application",
        });
    }

    return tables;
});

const baseColumns = [
    {
        name: "licence",
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
        label: "Quantity (m³/year)",
        align: "left",
        sortable: true,
    },
    {
        name: "flag",
        field: "qty_flag",
        label: "Flag",
        align: "center",
        sortable: true,
    }
]

const columns = [
    ...baseColumns, 
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
]

const tableFilters = [
    {
        label: "Source",
        options: [
            { label: "Surface Water", model: 'source', value: "sw" },
            { label: "Ground Water", model: 'source', value: "gw" },
        ],
    },
    {
        label: "Term",
        options: [
            { label: "Long", model: 'term', value: "long" },
            { label: "Short", model: 'term', value: "short" },
            { label: "Application", model: 'term', value: "app" },
        ],
    },
    {
        label: "Purpose",
        options: [
            { label: "Agriculture", model: 'purpose', value: "agriculture" },
            { label: "Commercial", model: 'purpose', value: "commercial" },
            { label: "Domestic", model: 'purpose', value: "domestic" },
            { label: "Municipal", model: 'purpose', value: "municipal" },
            { label: "Power", model: 'purpose', value: "power" },
            { label: "Oil & Gas", model: 'purpose', value: "oilgas" },
            { label: "Storage", model: 'purpose', value: "storage" },
            { label: "Other", model: 'purpose', value: "other" },
        ],
    },
]

const resetFilters = () => {
    filters.value = {
        source: {
            sw: true,
            gw: true,
        },
        term: {
            long: true,
            short: true,
            app: true,
        },
        purpose: {
            agriculture: true,
            commercial: true,
            domestic: true,
            municipal: true,
            power: true,
            oilgas: true,
            storage: true,
            other: true,
        },
        text: "",
    };
};
</script>

<style lang="scss" scoped>
.report-break {
    page-break-before: always;
}

.allocations-filter-menu {
    color: $primary-font-color;
    display: flex;
    flex-direction: column;

    .side-by-side {
        display: grid;
        grid-template-columns: 1fr 1fr;
    }
}
.report-header {
    padding: 1rem;

    &.surface-water-licence {
        background-color: #e0e9eb;
    }
    &.groundwater-licence {
        background-color: #cee5ea;
    }
    &.surface-water-application {
        background-color: #f1d1e6;
    }
    &.groundwater-application {
        background-color: #d1f1ed;
    }
}
.allocations-report-table {
    td, p {
        font-size: 10px !important; 
    }
    tr {
        page-break-inside: avoid;
    }
}
.allocations-container {
    td {
        align-content: start;
        &:first-child {
            max-width: 15vw;
        }
        p {
            margin-bottom: 0px !important;
        }
        .licence-box {
            border-radius: 5px;
            color: white;
            padding: 0.5em;
            text-align: center;

            &.sw-lic {
                background-color: #002d73;
            }
            &.sw-stu {
                background-color: #f7a800;
            }
            &.sw-app {
                background-color: #6f203e;
            }
            &.gw-lic {
                background-color: #29b6f6;
            }
            &.gw-stu {
                background-color: #ab47bc;
            }
            &.gw-app {
                background-color: #0f808f;
            }
        }
    }
}
</style>
