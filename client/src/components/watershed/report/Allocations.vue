<template>
    <div class="allocations-container">
        <h1 class="q-my-lg">Allocations</h1>
        <p>
            Water licences<NoteLink :note-number="21" /> and short term use
            approvals<NoteLink :note-number="20" /><sup>,</sup
            ><NoteLink :note-number="21" /> (collectively, ‘allocations’) for
            surface water and groundwater in British Columbia are managed under
            the Water Sustainability Act<NoteLink :note-number="10" />. These
            allocations are authorized by the Ministry of Forests, and the BC
            Energy Regulator (associated with activities regulated under the Oil
            and Gas Activities Act<NoteLink :note-number="11" />). Existing
            allocations, and active water licence applications<NoteLink
                :note-number="22"
            />
            within the query basin are summarized and listed in the charts and
            tables below.
        </p>
        <q-table
            v-if="props.reportContent.allocations.length > 0"
            :rows="filteredAllocations"
            :columns="columns"
            row-key="name"
            dense
            flat
            wrap-cells
        >
            <template #top>
                <h2 class="primary-font-text">
                    BC Water Sustainability Act - Water Licences -
                    {{ props.reportContent.allocations.length }} Licences,
                    {{
                        (+props.reportContent.annualHydrology.allocs_m3yr
                            .query).toFixed(1)
                    }}
                    m³ Total Annual Volume<NoteLink :note-number="9" />
                </h2>
                <q-btn icon="mdi-filter" flat class="primary-font-text">
                    <q-menu class="allocations-filter-menu q-pa-md">
                        <h3>Source</h3>
                        <q-checkbox
                            v-model="filters.source.gw"
                            label="Ground Water"
                        />
                        <q-checkbox
                            v-model="filters.source.sw"
                            label="Surface Water"
                        />

                        <h3>Term</h3>
                        <q-checkbox v-model="filters.term.long" label="Long" />
                        <q-checkbox
                            v-model="filters.term.short"
                            label="Short"
                        />
                        <q-checkbox
                            v-model="filters.term.app"
                            label="Application"
                        />

                        <h3>Purpose</h3>
                        <div class="side-by-side">
                            <q-checkbox
                                v-model="filters.purpose.agriculture"
                                label="Agriculture"
                            />
                            <q-checkbox
                                v-model="filters.purpose.commercial"
                                label="Commercial"
                            />
                        </div>
                        <div class="side-by-side">
                            <q-checkbox
                                v-model="filters.purpose.domestic"
                                label="Domestic"
                            />
                            <q-checkbox
                                v-model="filters.purpose.municipal"
                                label="Municipal"
                            />
                        </div>
                        <div class="side-by-side">
                            <q-checkbox
                                v-model="filters.purpose.power"
                                label="Power"
                            />
                            <q-checkbox
                                v-model="filters.purpose.oilgas"
                                label="Oil & Gas"
                            />
                        </div>
                        <div class="side-by-side">
                            <q-checkbox
                                v-model="filters.purpose.storage"
                                label="Storage"
                            />
                            <q-checkbox
                                v-model="filters.purpose.other"
                                label="Other"
                            />
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
            <template #body="props">
                <q-tr :props="props">
                    <td>
                        <p>{{ props.row.licensee }}</p>
                        <p>
                            {{ props.row.purpose }} from
                            {{ props.row.stream_name }} ({{
                                props.row.sourcetype
                            }})
                        </p>
                        <q-btn
                            v-if="props.row.file_no"
                            label="Licence Details"
                            icon="mdi-chevron-down"
                            dense
                            flat
                            color="blue-4"
                            no-caps
                            @click="toggleExpansion(props.row.fs_id)"
                        />
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
                            Start: {{ formatDate(new Date(props.row.start_date), 'dd mmm yyyy', ' ') }}
                        </p>
                        <p v-if="props.row.priority_date">
                            Priority: {{ formatDate(new Date(props.row.priority_date), 'dd mmm yyyy', ' ') }}
                        </p>
                        <p v-if="props.row.expiry_date">
                            Exp: {{ formatDate(new Date(props.row.expiry_date), 'dd mmm yyyy', ' ') }}
                        </p>
                        <p v-if="props.row.lic_status_date">
                            Status: {{ formatDate(new Date(props.row.lic_status_date), 'dd mmm yyyy', ' ') }}
                        </p>
                    </td>
                    <td>
                        {{ props.row.qty_display }}
                    </td>
                    <td>
                        {{ props.row.qty_flag }}
                    </td>
                    <td>
                        <div class="licence-box" :class="props.row.lic_type">
                            {{ props.row.lic_type }}
                        </div>
                    </td>
                    <td>
                        <q-icon
                            v-if="props.row.lic_status === 'CURRENT'"
                            name="mdi-check-circle"
                            size="sm"
                            color="green-5"
                        />
                    </td>
                </q-tr>
                <q-tr v-if="expandedIds.includes(props.row.fs_id)">
                    <td colspan="8" :style="{ 'background-color': '#efefef' }">
                        <p class="q-mb-none">Documents:</p>
                        <span
                            v-for="file in props.row.documentation"
                            :key="file.linkUrl"
                        >
                            {{ file.fileName }}:
                            <a :href="file.linkUrl" target="_blank">
                                {{ file.linkUrl }}
                            </a>
                        </span>
                    </td>
                </q-tr>
            </template>
        </q-table>
        <h2 v-else>No Allocations for selected watershed.</h2>
        <hr class="q-my-xl" />
    </div>
</template>

<script setup>
import NoteLink from "@/components/watershed/report/NoteLink.vue";
import { formatDate } from "@/utils/dateHelpers.js";
import { computed, ref } from "vue";

const props = defineProps({
    reportContent: {
        type: Object,
        default: () => {},
    },
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
        if (
            !filters.value.source.sw &&
            allocation.water_allocation_type === "SW"
        )
            return;
        if (
            !filters.value.source.gw &&
            allocation.water_allocation_type === "GW"
        )
            return;

        if (!filters.value.term.long && allocation.licence_term === "long")
            return;
        if (!filters.value.term.short && allocation.licence_term === "short")
            return;
        if (
            !filters.value.term.app &&
            allocation.licence_term === "application"
        )
            return;

        if (
            !filters.value.purpose.agriculture &&
            allocation.purpose_groups === "Agriculture"
        )
            return;
        if (
            !filters.value.purpose.commercial &&
            allocation.purpose_groups === "Commercial"
        )
            return;
        if (
            !filters.value.purpose.domestic &&
            allocation.purpose_groups === "Domestic"
        )
            return;
        if (
            !filters.value.purpose.municipal &&
            allocation.purpose_groups === "Municipal"
        )
            return;
        if (
            !filters.value.purpose.power &&
            allocation.purpose_groups === "Power"
        )
            return;
        if (
            !filters.value.purpose.oilgas &&
            allocation.purpose_groups === "Oil & Gas"
        )
            return;
        if (
            !filters.value.purpose.storage &&
            allocation.purpose_groups === "Storage"
        )
            return;
        if (
            !filters.value.purpose.other &&
            allocation.purpose_groups === "Other"
        )
            return;

        if (filters.value.text.length > 0) {
            if (!allocation.licensee.includes(filters.value.text)) return;
        }

        myAllocations.push(allocation);
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
        align: "center",
        sortable: true,
    },
];

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

const expandedIds = ref([]);
const toggleExpansion = (id) => {
    if (expandedIds.value.includes(id)) {
        expandedIds.value.splice(expandedIds.value.indexOf(id), 1);
    } else {
        expandedIds.value.push(id);
    }
};
</script>

<style lang="scss">
.allocations-filter-menu {
    color: $primary-font-color;
    display: flex;
    flex-direction: column;

    .side-by-side {
        display: grid;
        grid-template-columns: 1fr 1fr;
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
