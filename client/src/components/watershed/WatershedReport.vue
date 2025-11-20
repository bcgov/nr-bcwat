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
            <div id="header" class="text-h6 q-ml-md">{{ props.reportContent.overview.watershedName }}</div>
            <q-separator
                class="q-my-md"
                color="white"
            />
            <div class="sidebar-contents">
                <q-list dense>
                    <template
                        v-for="section in sections"
                        :key="section.id"
                    >
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
                <div class="download-btn-container">
                    <q-btn
                        label="Download Polygon"
                        color="primary"
                        dense
                        :loading="polygonLoading"
                        @click="polygonDownloadOpen = true"
                    />
                    <q-btn
                        class="q-mt-sm"
                        label="Download PDF"
                        color="primary"
                        dense
                        :loading="pdfLoading"
                        @click="pdfDownload()"
                    />
                </div>
                <q-dialog
                    v-model="polygonDownloadOpen"
                >
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
                                Use the following options to download the query watershed polygon:  
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
        <div 
            class="report-content"
            ref="pdfReport"
        >
            <template
                v-for="section in sections"
                :key="section.id"
            >
                <component
                    v-if="section.enabled"
                    :id="section.id"
                    :is="section.component"
                :is-pdf="isPdf"
                    :report-content="reportContent"
                    :clicked-point="clickedPoint"
                    :wfi="props.wfi"
                    class="report-component"
                />
                <q-separator 
                    v-if="!isPdf"
                    class="q-my-xl"
                />
            </template>
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
import FutureHydrologicVariability from "@/components/watershed/report/FutureHydrologicVariability.vue"
import Landcover from "@/components/watershed/report/Landcover.vue";
import Climate from "@/components/watershed/report/Climate.vue";
import Topography from "@/components/watershed/report/Topography.vue";
import Notes from "@/components/watershed/report/Notes.vue";
import References from "@/components/watershed/report/References.vue";
import Methods from "@/components/watershed/report/Methods.vue";
import { nextTick, onMounted, ref, useTemplateRef } from "vue";
import html2pdf from 'html2pdf.js';
import dayjs from 'dayjs';
import { downloadWatershedReportPolygon } from "@/utils/api";

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
        required: true
    }
});

const emit = defineEmits(["close"]);

const sections = [
    {
        label: "Overview",
        id: "overview",
        component: WatershedOverview,
        enabled: props.reportContent.sectionsAvailable.overview
    },
    {
        label: "Introduction",
        id: "introduction",
        component: WatershedIntroduction,
        enabled: props.reportContent.sectionsAvailable.introduction
    },
    {
        label: "Annual Hydrology",
        id: "annual_hydrology",
        component: AnnualHydrology,
        enabled: props.reportContent.sectionsAvailable.annualHydrology
    },
    {
        label: "Monthly Hydrology",
        id: "monthly_hydrology",
        component: MonthlyHydrology,
        enabled: props.reportContent.sectionsAvailable.monthlyHydrology
    },
    {
        label: "Allocations by Industry",
        id: "allocations_by_industry",
        component: AllocationsByIndustry,
        enabled: props.reportContent.sectionsAvailable.allocationsByIndustry
    },
    {
        label: "Allocations",
        id: "allocations",
        component: Allocations,
        enabled: props.reportContent.sectionsAvailable.allocations
    },
    {
        label: "Hydrologic Variability",
        id: "hydrologic_variability",
        component: HydrologicVariability,
        enabled: props.reportContent.sectionsAvailable.hydrologicVariability
    },
    {
        label: "Future Hydrologic Variability",
        id: "future_hydrologic_variability",
        component: FutureHydrologicVariability,
        enabled: props.reportContent.sectionsAvailable.futureHydrologicVariability
    },
    {
        label: "Landcover",
        id: "landcover",
        component: Landcover,
        enabled: props.reportContent.sectionsAvailable.landcover
    },
    {
        label: "Climate",
        id: "climate",
        component: Climate,
        enabled: props.reportContent.sectionsAvailable.climate
    },
    {
        label: "Topography",
        id: "topography",
        component: Topography,
        enabled: props.reportContent.sectionsAvailable.topography
    },
    {
        label: "Notes",
        id: "notes",
        component: Notes,
        enabled: props.reportContent.sectionsAvailable.notes
    },
    {
        label: "References",
        id: "references",
        component: References,
        enabled: props.reportContent.sectionsAvailable.references
    },
    {
        label: "Methods",
        id: "methods",
        component: Methods,
        enabled: props.reportContent.sectionsAvailable.methods
    },
];

let sectionObserver = null;
const activeSection = ref();
const observeOn = ref(true);
const polygonDownloadOpen = ref(false);
const polygonDownloadType = ref('geojson');
const polygonLoading = ref(false);
const pdfReport = useTemplateRef('pdfReport');
const isPdf = ref(false);

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
const shpLoading = ref(false);

const downloadPolygon = async (type) => {
    polygonLoading.value = true;
    try{
        if(type){
            const response = await downloadWatershedReportPolygon(props.wfi, type);
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            // simple programatic download element and event
            const a = document.createElement('a');
            a.href = url;
            a.download = props.reportContent.overview.mgmt_name;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
    } catch (e) {
        console.error(e)
    } finally {
        polygonLoading.value = false;
    }
}

const pdfDownload = async () => {
    const element = pdfReport.value;
    isPdf.value = true;
 
    try{
        const prom = new Promise((res, rej) => {
            const dateString = dayjs().format('M-D-YYYY');
            const options = {
                margin: 0.5,
                filename: `${props.reportContent.overview.watershedName}-${props.wfi}-${dateString}.pdf`,
                image: { type: 'jpeg', quality: 1 },
                html2canvas: { 
                    scale: 1,
                    dpi: 192,
                    letterRendering: true, 
                    onclone: (clonedDoc) => {
                        clonedDoc.isPdf = true;
                        resizeTablesForPDF(clonedDoc);
                    }
                },
                pagebreak: { after: '.report-break', avoid: ["table", "svg"] },
                jsPDF: { unit: 'in', format: 'a4', orientation: 'portrait' },
            };

            // Use html2pdf with pagebreak settings
            html2pdf().set(options).from(element).save();
            return res;
        })

        await prom.then(() => {
            console.log('JOB DONE')
            isPdf.value = false;
        });
    } catch(e) {
        console.error(e);
    } finally {
        isPdf.value = false;
    }
}

const resizeTablesForPDF = (clonedDoc) => {
    
};
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

