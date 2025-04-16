<template>
    <div
        class="report-container row"
        :class="props.reportOpen ? 'open' : ''"
    >
        <div class="sidebar">
            <q-btn
                class="q-mb-md"
                color="white"
                flat
                label="Back to Map"
                icon="reply"
                dense
                @click="() => emit('close')"
            />
            <p>{{ props.activePoint?.nid }}</p>
            <hr :style="{'width': '100%'}">
            <q-list dense>
                <q-item
                    v-for="section in sections"
                    :key="section.id"
                    clickable
                    :focused="section.id === activeSection"
                    @click="scrollToSection(section.id)"
                >
                    <q-item-section>
                        <b>{{ section.label }}</b>
                    </q-item-section>
                </q-item>
            </q-list>
        </div>
        <div class="report-content">
            <component 
                v-for="section in sections"
                :key="section.id"
                :is="section.component"
                :id="section.id"
            />
        </div>
    </div>
</template>

<script setup>
import WatershedOverview from "@/components/watershed/report/WatershedOverview.vue";
import WatershedIntroduction from "@/components/watershed/report/WatershedIntroduction.vue";
import AnnualHydrology from "@/components/watershed/report/AnnualHydrology.vue";
import MonthlyHydrology from "@/components/watershed/report/MonthlyHydrology.vue";
import AllocationsByIndustry from "@/components/watershed/report/AllocationsByIndustry.vue";
import Allocations from "@/components/watershed/report/Allocations.vue";
import HydrologicVariability from "@/components/watershed/report/HydrologicVariability.vue";
import Landcover from "@/components/watershed/report/Landcover.vue";
import Climate from "@/components/watershed/report/Climate.vue";
import Topography from "@/components/watershed/report/Topography.vue";
import Notes from "@/components/watershed/report/Notes.vue";
import References from "@/components/watershed/report/References.vue";
import Methods from "@/components/watershed/report/Methods.vue";
import { ref } from 'vue';

const props = defineProps({
    reportOpen: {
        type: Boolean,
        default: false,
    },
    activePoint: {
        type: Object,
        default: () => {},
    },
});

const emit = defineEmits(["close"]);

const sections = [
    {
        label: 'Overview',
        id: 'overview',
        component: WatershedOverview,
    },
    {
        label: 'Introduction',
        id: 'introduction',
        component: WatershedIntroduction,
    },
    {
        label: 'Annual Hydrology',
        id: 'annual_hydrology',
        component: AnnualHydrology,
    },
    {
        label: 'Monthly Hydrology',
        id: 'monthly_hydrology',
        component: MonthlyHydrology,
    },
    {
        label: 'Allocations by Industry',
        id: 'allocations_by_industry',
        component: AllocationsByIndustry,
    },
    {
        label: 'Allocations',
        id: 'allocations',
        component: Allocations,
    },
    {
        label: 'Hydrologic Variability',
        id: 'hydrologic_variability',
        component: HydrologicVariability,
    },
    {
        label: 'Landcover',
        id: 'landcover',
        component: Landcover,
    },
    {
        label: 'Climate',
        id: 'climate',
        component: Climate,
    },
    {
        label: 'Topography',
        id: 'topography',
        component: Topography,
    },
    {
        label: 'Notes',
        id: 'notes',
        component: Notes,
    },
    {
        label: 'References',
        id: 'references',
        component: References,
    },
    {
        label: 'Methods',
        id: 'methods',
        component: Methods,
    },
];

const activeSection = ref();

/**
 * Scroll report to selected component id
 * @param id id of component to scroll to
 */
const scrollToSection = (id) => {
    activeSection.value = id;
    document.getElementById(id).scrollIntoView({ block: 'start',  behavior: 'smooth' });
}
</script>

<style lang="scss" scoped>
.spaced-flex-row {
    padding: 1em;
}
</style>
