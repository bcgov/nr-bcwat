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
        <div id="header" class="text-h6 q-ml-md">
            {{ props.reportContent.overview.watershedName }}
        </div>
        <q-separator class="q-my-md" color="white" />
        <div class="sidebar-contents">
            <q-list dense>
            <template v-for="section in sections" :key="section.id">
                <q-item
                    v-if="section.enabled"
                    :key="section.id"
                    clickable
                    :focused="section.id === activeSection"
                    @click="scrollToSection(section.id)"
                >
                <q-item-section>
                    <b>{{ section.label }}</b>
                </q-item-section>
                </q-item>
            </template>
            </q-list>
            <div class="download-btn-container" style="gap: 5px">
            <q-btn
                label="Download Polygon"
                color="primary"
                dense
                :loading="polygonLoading"
                @click="polygonDownloadOpen = true"
            />
            <q-btn
                label="Download PDF"
                color="primary"
                dense
                :loading="pdfLoading"
                @click="showCustomizePdfModal = true"
            />
            <q-btn
                label="Download CSV"
                color="primary"
                dense
                :loading="csvLoading"
                @click="downloadCsv"
            />
            </div>
            <q-dialog v-model="polygonDownloadOpen">
            <q-card>
                <q-card-section class="bg-primary text-white">
                <div class="download-header">
                    <div class="text-h6">Download Query Watershed Polygon</div>
                    <q-btn
                        icon="close"
                        flat
                        size="sm"
                        @click="polygonDownloadOpen = false"
                    />
                </div>
                </q-card-section>
                <q-card-section>
                <p class="q-mb-none">
                    Use the following options to download the query watershed
                    polygon:
                </p>
                </q-card-section>
                <q-card-actions align="around">
                <div class="download-btn-container">
                    <q-radio
                        v-model="polygonDownloadType"
                        val="geojson"
                        label="GeoJSON (.geojson)"
                    />
                    <q-radio
                        v-model="polygonDownloadType"
                        val="shapefile"
                        label="Shapefile (.shp)"
                    />
                </div>
                <q-btn
                    class="full-width"
                    color="primary"
                    @click="downloadPolygon(polygonDownloadType)"
                >
                    download
                </q-btn>
                </q-card-actions>
            </q-card>
            </q-dialog>
        </div>
        </div>
        <div class="report-content">
            <template 
                v-for="section in sections" 
                :key="section.id"
            >
                <component
                    v-if="section.enabled"
                    :id="section.id"
                    :is="section.component"
                    :report-content="reportContent"
                    :clicked-point="clickedPoint"
                    :points="points"
                    class="report-component"
                />
            </template>
            <WatershedCustomizationModal
                :show-modal="showCustomizePdfModal"
                :report-sections="sections"
                show-title-field
                show-notes-field
                modal-title="Customize your PDF report"
                report-type="pdf"
                :default-report-title="userPdfTitle"
                @download-report="pdfDownload"
                @close-modal="showCustomizePdfModal = false"
            />
        </div>
    </div>
</template>

<script setup>
import { downloadCsvWatershedReport } from "@/utils/api.js";
import { Notify } from "quasar";
import download from "downloadjs";
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
import WatershedCustomizationModal from "@/components/watershed/WatershedCustomizationModal.vue";
import { reportFileName } from "@/utils/reportHelpers.js";
import {
    downloadWatershedReportPolygon,
    getWatershedReportPdf,
} from "@/utils/api";
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
    wfi: {
        type: String,
        required: true,
    },
    points: {
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
        enabled: props.reportContent.sectionsAvailable.overview,
    },
    {
        label: "Introduction",
        id: "introduction",
        component: WatershedIntroduction,
        enabled: props.reportContent.sectionsAvailable.introduction,
    },
    {
        label: "Annual Hydrology",
        id: "annualHydrology",
        component: AnnualHydrology,
        enabled: props.reportContent.sectionsAvailable.annualHydrology,
    },
    {
        label: "Monthly Hydrology",
        id: "monthlyHydrology",
        component: MonthlyHydrology,
        enabled: props.reportContent.sectionsAvailable.monthlyHydrology,
    },
    {
        label: "Allocations",
        id: "allocations",
        component: Allocations,
        enabled: props.reportContent.sectionsAvailable.allocations,
    },
    {
        label: "Allocations by Industry",
        id: "allocationsByIndustry",
        component: AllocationsByIndustry,
        enabled: props.reportContent.sectionsAvailable.allocationsByIndustry,
    },
    {
        label: "Hydrologic Variability",
        id: "hydrologicVariability",
        component: HydrologicVariability,
        enabled: props.reportContent.sectionsAvailable.hydrologicVariability,
    },
    {
        label: "Landcover",
        id: "landcover",
        component: Landcover,
        enabled: props.reportContent.sectionsAvailable.landcover,
    },
    {
        label: "Climate",
        id: "climate",
        component: Climate,
        enabled: props.reportContent.sectionsAvailable.climate,
    },
    {
        label: "Topography",
        id: "topography",
        component: Topography,
        enabled: props.reportContent.sectionsAvailable.topography,
    },
    {
        label: "Notes",
        id: "notes",
        component: Notes,
        enabled: props.reportContent.sectionsAvailable.notes,
    },
    {
        label: "References",
        id: "references",
        component: References,
        enabled: props.reportContent.sectionsAvailable.references,
    },
    {
        label: "Methods",
        id: "methods",
        component: Methods,
        enabled: props.reportContent.sectionsAvailable.methods,
    },
];

let sectionObserver = null;
const activeSection = ref();
const observeOn = ref(true);
const polygonDownloadOpen = ref(false);
const polygonDownloadType = ref("geojson");
const polygonLoading = ref(false);
const csvLoading = ref(false);
const showCustomizePdfModal = ref(false);
const userPdfTitle = ref("Watershed Summary");

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
        // Handle Null Element for now
        const el = document.getElementById(section.id);
        if (el) {
            sectionObserver.observe(el);
        } else {
            console.warn(`Could not find element with id ${section.id}`);
        }
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

const pdfLoading = ref(false);

const downloadPolygon = async (type) => {
    polygonLoading.value = true;
    try {
        if (type) {
            const response = await downloadWatershedReportPolygon(props.wfi, type);
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            // simple programatic download element and event
            const a = document.createElement("a");
            a.href = url;
            a.download = props.reportContent.overview.mgmt_name;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
    } catch (e) {
        console.error(e);
    } finally {
        polygonLoading.value = false;
    }
};

const pdfDownload = async (userCustomization) => {
    try {
        showCustomizePdfModal.value = false;
        pdfLoading.value = true;

        // get PDF file buffer
        const apiResponse = await getWatershedReportPdf(
            props.clickedPoint,
            props.wfi,
            props.reportContent.overview.watershedName,
            userCustomization.title || "Watershed Summary",
            userCustomization.notes || "",
            userCustomization
        );

        if(apiResponse !== null){
        // trigger download in browser
        const pdfFileName = reportFileName(userCustomization.title, "watershed_report");
        download(apiResponse, `${pdfFileName}_wfi_${props.wfi}.pdf`);

        Notify.create({
            message: "Your PDF report is ready to download.",
            type: "positive",
        });
        } else {
            throw new Error("Failed to generate PDF");
        }
    } catch (e) {
        Notify.create({
            message: `${e}: There was a problem generating a PDF for this report.`,
            type: "negative",
        });
    } finally {
        pdfLoading.value = false;
    }
};

const downloadCsv = async () => {
    csvLoading.value = true;
    await downloadCsvWatershedReport(props.wfi);
    csvLoading.value = false;
}
</script>

<style lang="scss">
.sidebar-contents {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 100%;
}
.download-header {
    display: flex;
    justify-content: space-between;
}
.download-btn-container {
    display: flex;
    flex-direction: column;
    .q-btn {
        width: 100%;
    }
}
</style>
