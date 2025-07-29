<template>
    <div class="report-container" :class="props.reportOpen ? 'open' : ''">
        <div class="report-sidebar">
            <q-btn
                class="q-mb-md"
                color="white"
                flat
                label="Back to Map"
                icon="reply"
                dense
                @click="() => emit('close')"
            />
            <div class="text-h6">{{ props.reportContent.overview.watershedName }}</div>
            <q-separator
                class="q-my-md"
                color="white"
            />
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
            <q-btn label="Download" color="primary" dense />
        </div>
        <div class="report-content">
            <component
                v-for="section in sections"
                :key="section.id"
                :id="section.id"
                :is="section.component"
                :report-content="reportContent"
                :clicked-point="clickedPoint"
                class="report-component"
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
import { onMounted, ref } from "vue";

const props = defineProps({
    reportOpen: {
        type: Boolean,
        default: false,
    },
    reportContent: {
        type: Object,
        default: () => {},
    },
    clickedPoint: {
        type: Object,
        default: () => {},
    },
});

const emit = defineEmits(["close"]);

const sections = [
    {
        label: "Overview",
        id: "overview",
        component: WatershedOverview,
    },
    {
        label: "Introduction",
        id: "introduction",
        component: WatershedIntroduction,
    },
    // {
    //     label: "Annual Hydrology",
    //     id: "annual_hydrology",
    //     component: AnnualHydrology,
    // },
    // {
    //     label: "Monthly Hydrology",
    //     id: "monthly_hydrology",
    //     component: MonthlyHydrology,
    // },
    {
        label: "Allocations by Industry",
        id: "allocations_by_industry",
        component: AllocationsByIndustry,
    },
    {
        label: "Allocations",
        id: "allocations",
        component: Allocations,
    },
    // {
    //     label: "Hydrologic Variability",
    //     id: "hydrologic_variability",
    //     component: HydrologicVariability,
    // },
    {
        label: "Landcover",
        id: "landcover",
        component: Landcover,
    },
    {
        label: "Climate",
        id: "climate",
        component: Climate,
    },
    {
        label: "Topography",
        id: "topography",
        component: Topography,
    },
    {
        label: "Notes",
        id: "notes",
        component: Notes,
    },
    {
        label: "References",
        id: "references",
        component: References,
    },
    {
        label: "Methods",
        id: "methods",
        component: Methods,
    },
];

let sectionObserver = null;
const activeSection = ref();
const observeOn = ref(true);

onMounted(() => {
    observeSections();
    setTimeout(() => {
        activeSection.value = "overview";
    }, 10);
});

/**
 * Create an observer for each section in the report.
 */
const observeSections = () => {
    try {
        sectionObserver.disconnect();
    } catch {
        // ignore errors?
    }

    const options = {
        rootMargin: "40px 0px",
        threshold: 0.1,
        root: null,
    };
    sectionObserver = new IntersectionObserver(sectionObserverHandler, options);

    // Observe each section
    sections.forEach((section) => {
        sectionObserver.observe(document.getElementById(section.id));
    });
};

/**
 * Update active section id when a section comes into view
 *
 * @param {*} entries entries to compare url to
 */
const sectionObserverHandler = (entries) => {
    if (!observeOn.value) return;
    for (const entry of entries) {
        const sectionId = entry.target.id;
        if (entry.isIntersecting) activeSection.value = sectionId;
    }
};

/**
 * Scroll report to selected component id
 * @param id id of component to scroll to
 */
const scrollToSection = (id) => {
    observeOn.value = false;
    activeSection.value = id;
    document.getElementById(id).scrollIntoView({
        block: "start",
        behavior: "smooth",
        inline: "nearest",
    });
    setTimeout(() => {
        observeOn.value = true;
    }, 1000);
};
</script>

<style lang="scss" scoped>
.spaced-flex-row {
    padding: 1em;
}
</style>
