<template>
    <div
        v-if="reportContent"
        class="static-report-layout"
        @click="pdfDownload()"
    >
    <!-- <pre>{{ reportContent }}</pre> -->
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
    <div v-else>
        WAIT FOR REPORT TO DOWNLOAD
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
import { getWatershedReportByWFI } from '@/utils/api.js';
import { onMounted, ref } from "vue";
import { useRoute } from 'vue-router';
import html2pdf from 'html2pdf.js';


const route = useRoute();

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
    {
        label: "Annual Hydrology",
        id: "annual_hydrology",
        component: AnnualHydrology,
    },
    {
        label: "Monthly Hydrology",
        id: "monthly_hydrology",
        component: MonthlyHydrology,
    },
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
    {
        label: "Hydrologic Variability",
        id: "hydrologic_variability",
        component: HydrologicVariability,
    },
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

const reportContent = ref();
const clickedPoint = ref();
onMounted(async () => {
    clickedPoint.value = { lat: route.query.lat, lng: route.query.lng };
    reportContent.value = await getWatershedReportByWFI(route.query.wfi);
    setTimeout(() => {
        // pdfDownload();
    }, 2000);
});

const pdfDownload = () => {
    console.log("EXECUTE NOW!")

    const elements = [].slice.call(document.getElementsByClassName('report-component'));

    const pdfOptions = {
        // enableLinks: false,
        filename: `first_try.pdf`,
        html2canvas: {scale: 2},
        image: {type: 'png'},
        jsPDF: {format: 'letter', orientation: 'portrait', compress: true,},
        pagebreak: { mode: ['avoid-all', 'css', 'legacy'] },
        margin: 8,
    }

    let worker = html2pdf().set(pdfOptions).from(elements[0]);

    console.log(elements)

    if (elements.length > 1) {
        worker = worker.toPdf();

        elements.slice(1).forEach(async element => {
            worker = worker
                .get('pdf')
                .then(pdf => {
                    pdf.addPage();
                })
                .from(element)
                .toContainer()
                .toCanvas()
                .toPdf();
        });

        console.log("SAVE")
        worker.save().then(() => {
            console.log("MISSION COMPREE")
        })
    }

};
</script>

<style lang="scss">
@page {
    margin: 48px;
}
.static-report-layout {
    position: relative;
    print-color-adjust: exact;
    -webkit-print-color-adjust: exact;

    // use a static width for the whole report
    width: 720px; // 8.5inch - (2 * 48px margins) // Was 720
    overflow: hidden;
    // center-align content for development
    margin: 0 auto;

    .content li + li {
        margin-top: 0.67rem;
    }

    .content:not(:last-child) {
        margin-bottom: 1.33rem;
    }

    .page-break-before {
        page-break-before: always;
    }

    .page-break-after {
        page-break-after: always;
    }

    .pdf-no-top-spacing {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    .pdf-add-top-margin {
        margin-top: 1.25rem;
    }

    .pdf-no-bottom-spacing {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }

    .report-main {
        margin: 0;
    }

    .report-section {
        page-break-inside: avoid;
        border-bottom: none;

        .header {
            margin-bottom: 1.25rem;

            .header-text {
                padding: 1.25rem;
                // background-color: $pdf-report-section-header-background;

                .title {
                    // color: $pdf-report-section-title-color;
                    font-size: 1.875rem;
                    font-weight: bold;

                    a {
                        color: inherit;
                    }

                }
                .subtitle {
                    // color: $pdf-report-section-title-color;
                }
            }
        }

        p {
            line-height: 1.25rem;
            margin-bottom: 1rem;
        }

        .section-content {
            margin: 0 1.25rem;
        }

        // footer elements
        .footer {
            padding: 2rem 1.5rem 2rem;
            font-size: 0.7em;

            p:last-child {
                margin: 0;
            }
        }
    }
    
    .hydrologic-watershed-table {
        width: 500px !important;
    }
}
.spaced-flex-row {
    padding: 1em;
}
</style>
