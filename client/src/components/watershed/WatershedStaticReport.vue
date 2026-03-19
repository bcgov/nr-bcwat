<template>
    <div id="watershed-static-report" class="watershed static report">
        <!-- Set properties for the static report component and its child components -->
        <StaticReport
            v-if="!!reportData && !!sections"
            :report-content="reportData"
            :points="points"
            :sections="sections"
            :removed-sections="removedSections"
            @load="loadSection"
        />
    </div>
</template>

<script setup>
import { LngLat } from "maplibre-gl";
import StaticReport from "@/components/watershed/report/StaticReport.vue";
import StaticReportTableOfContents from "@/components/watershed/report/StaticReportTableOfContents.vue";
import AllocationsByIndustry from "@/components/watershed/report/AllocationsByIndustry.vue";
import AnnualHydrology from "@/components/watershed/report/AnnualHydrology.vue";
import Climate from "@/components/watershed/report/Climate.vue";
import HydrologicVariability from "@/components/watershed/report/HydrologicVariability.vue";
import WatershedIntroduction from "@/components/watershed/report/WatershedIntroduction.vue";
import Landcover from "@/components/watershed/report/Landcover.vue";
import Methods from "@/components/watershed/report/Methods.vue";
import MonthlyHydrology from "@/components/watershed/report/MonthlyHydrology.vue";
import Notes from "@/components/watershed/report/Notes.vue";
import WatershedOverview from "@/components/watershed/report/WatershedOverview.vue";
import References from "@/components/watershed/report/References.vue";
import ReportCover from "@/components/watershed/report/ReportCover.vue";
import Allocations from "@/components/watershed/report/Allocations.vue";
import Topography from "@/components/watershed/report/Topography.vue";
import {
  getWatershedReportByWFI,
  getAllWatershedLicences,
} from "@/utils/api.js";
import { computed, nextTick, onMounted, ref } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();

// request parameters
const fwa = ref(null);
const lngLat = ref(null);
const watershedName = ref(null);
const wfi = ref(null);
const userTitle = ref(null);
const userNotes = ref(null);
const userSections = ref(null);
const reportCoverMapLoaded = ref(false);
const removedSections = ref([]);
// empty array that can store all promises for options pdf sections
const optionalSectionPromises = ref([]);
// define pageLoadPromise for the PDF converter service
const dataLoaded = ref(false);
const points = ref([]);

// data from API
const reportData = ref(null);

const sections = computed(() => {
    const coverSections = [
        {
            title: "Report Cover",
            id: "reportCover",
            sectionComponent: ReportCover,
            classes: "pdf-no-bottom-spacing",
            enabled: true
        },
        {
            title: "Table of Contents",
            id: "reportToc",
            sectionComponent: StaticReportTableOfContents,
            classes: "pdf-no-bottom-spacing page-break-after",
            enabled: true
        },
    ];

    const optionalSections = [
        {
            title: "Introduction",
            id: "introduction",
            sectionComponent: WatershedIntroduction,
            enabled: reportData.value?.sectionsAvailable?.introduction
        },
        {
            title: "Overview",
            id: "overview",
            sectionComponent: WatershedOverview,
            enabled: reportData.value?.sectionsAvailable.overview
        },
        {
            title: "Annual Hydrology",
            id: "annualHydrology",
            sectionComponent: AnnualHydrology,
            classes: "pdf-no-bottom-spacing",
            enabled: reportData.value?.sectionsAvailable.annualHydrology
        },
        {
            title: "Monthly Hydrology",
            id: "monthlyHydrology",
            sectionComponent: MonthlyHydrology,
            enabled: reportData.value?.sectionsAvailable.monthlyHydrology
        },
        {
            title: "Allocations",
            id: "allocations",
            sectionComponent: Allocations,
            enabled: reportData.value?.sectionsAvailable.allocations
        },
        {
            title: "Allocations By Industry",
            id: "allocationsByIndustry",
            sectionComponent: AllocationsByIndustry,
            classes: "pdf-no-bottom-spacing",
            enabled: reportData.value?.sectionsAvailable.allocationsByIndustry
        },
        {
            title: 'Hydrologic Variability',
            id: 'hydrologicVariability',
            sectionComponent: HydrologicVariability,
            classes: 'pdf-no-bottom-spacing page-break-after',
            enabled: reportData.value?.sectionsAvailable.hydrologicVariability
        },
        {
            title: 'Landcover',
            id: 'landcover',
            sectionComponent: Landcover,
            classes: 'page-break-after',
            enabled: reportData.value?.sectionsAvailable.landcover
        },
        {
            title: 'Climate',
            id: 'climate',
            sectionComponent: Climate,
            classes: 'pdf-no-bottom-spacing',
            enabled: reportData.value?.sectionsAvailable.climate
        },
        {
            title: 'Topography',
            id: 'topography',
            sectionComponent: Topography,
            enabled: reportData.value?.sectionsAvailable.topography
        },
        {
            title: 'Notes',
            id: 'notes',
            sectionComponent: Notes,
            enabled: reportData.value?.sectionsAvailable.notes
        },
        {
            title: 'References',
            id: 'references',
            sectionComponent: References,
            enabled: reportData.value?.sectionsAvailable.references
        },
        {
            title: 'Methods',
            id: 'methods',
            sectionComponent: Methods,
            enabled: reportData.value?.sectionsAvailable.methods
        }
    ];

    // compare user selected sections with optional sections and match the id's for the sections
    // that have been selected by the user
    let outputSections = optionalSections;
    const includedSections = (JSON.parse(route.query.userCustomization))
    if (userSections.value) {
        outputSections = optionalSections.filter((section) => {
            if(includedSections.sections.includes(section.id) || section.isHeader){
                return true;
            }
        });
    }

    // combine the cover page section with the optional sections
    return [...coverSections, ...outputSections];
});

// report customizations on user title and notes
const userCustomization = computed(() => {
    return {
        userTitle: userTitle.value,
        userNotes: userNotes.value,
    };
});

const sectionsLoaded = computed(() => {
    const loadedSections = [
        dataLoaded.value,
        reportCoverMapLoaded.value,
        ...optionalSectionPromises.value,
    ].map((el) => {
        return el == true;
    });
    return loadedSections;
});

onMounted(() => {
    // parse query parameters
    fwa.value = route.query.fwa;
    const lat = route.query.lat;
    const lng = route.query.lng;
    const title = route.query.title || "Watershed Summary";
    const notes = route.query.notes || "";
    watershedName.value = route.query.watershedName;
    wfi.value = route.query.wfi;
    lngLat.value = new LngLat(lng, lat);
    userTitle.value = title;
    userNotes.value = notes;
    userSections.value = sections.value;

    // promises to track individual sections loading
    // (sections with asynchronous maps, etc.)
    // optional sections controlled by user checkboxes are compared with selected sections

    // resolves when the page is ready for PDF snapshot
    window.pageLoadPromise = sectionsLoaded.value;

    // fetch data from API
    getData();

    // check that section has been included by the user in the pdf report
    if (userSections.value.includes("annualHydrology")) {
        optionalSectionPromises.push("annualHydrology");
    }
    if (userSections.value.includes("hydrologicVariability")) {
        optionalSectionPromises.push("hydrologicVariability");
    }
});

/**
 * fetch all required report data from the API
 */
const getData = async () => {
    try {
        // load the watershed report information
        const apiResponse = await getWatershedReportByWFI(wfi.value);
        points.value = await getAllWatershedLicences();

        reportData.value = {
            ...apiResponse,
            // add click location to reportData
            lngLat: lngLat.value,
            // add ToC info to reportData
            sections: sections.value,
            userCustomization: userCustomization.value,
        };

        // emit event to resolve dataLoaded promise
        nextTick(() => {
            dataLoaded.value = true;
        });
    } catch (e) {
        // cause the dataLoaded promise to reject
        dataLoaded.value = false;
        // re-throw to error handlers
        throw e;
    }
};

const loadSection = (sectionId) => {
    if (sectionId === "reportCover") {
        // report cover section is always included in the pdf report
        reportCoverMapLoaded.value = true;
    }
};
</script>

<style lang="scss">
.watershed.static.report {
  display: unset;
  grid-template-columns: unset;
  position: unset;
  width: unset;
  font-size: 0.9em;

  .static-allocations-table-section {
    td {
      .licence {
        width: 230px;
        white-space: normal;
      }

      .quantity {
        white-space: normal;
      }
    }
  }
}
</style>
