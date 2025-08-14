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
            <div class="text-h6 q-ml-md">{{ props.reportContent.overview.watershedName }}</div>
            <q-separator
                class="q-my-md"
                color="white"
            />
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
            <q-btn
                label="Download PDF"
                color="primary"
                dense
                :loading="pdfLoading"
                @click="pdfDownload()"
            />
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
                    class="report-component"
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
import { onMounted, ref } from "vue";
import html2pdf from 'html2pdf.js';

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

const resizeS3ForPDF = (elements, targetElementIds, width) => {

    const originalStates = []

    elements.forEach(element => {
        targetElementIds.forEach(elementId => {
            // Find the container by ID
            const container = element.querySelector(`#${elementId}`);
            if (container) {
                // Look for SVG first
                const svg = container.querySelector('svg');
                if (svg) {
                    const originalState = {
                        type: 'svg',
                        element: svg,
                        container: container,
                        elementId: elementId,
                        width: svg.getAttribute('width'),
                        height: svg.getAttribute('height'),
                        styleWidth: svg.style.width,
                        styleHeight: svg.style.height,
                        containerStyleWidth: container.style.width,
                        containerStyleHeight: container.style.height
                    };
                    originalStates.push(originalState);


                    const currentWidth = parseFloat(svg.getAttribute('width'));
                    const currentHeight = parseFloat(svg.getAttribute('height'));

                    if (currentWidth > width) {
                        const aspectRatio = currentHeight / currentWidth;
                        const newWidth = width;
                        const newHeight = newWidth * aspectRatio;

                        svg.setAttribute('width', newWidth);
                        svg.setAttribute('height', newHeight);
                        svg.style.width = newWidth + 'px';
                        svg.style.height = newHeight + 'px';

                        if (!svg.getAttribute('viewBox')) {
                            svg.setAttribute('viewBox', `0 0 ${currentWidth} ${currentHeight}`);
                        }
                    }
                }
            }
        });
    });

    return originalStates
};

function resizeTablesForPDF(clonedDoc) {
  // target only the legend tables (add more selectors if needed)
  const targets = [
    { sel: '#monthly-hydrology-legend table', max: 400 },
    { sel: '#monthly-hydrology-table table', max: 700}
  ];

  targets.forEach(({ sel, max }) => {
    clonedDoc.querySelectorAll(sel).forEach((table) => {
      table.style.width = '100%';
      table.style.maxWidth = `${max}px`;
      table.style.tableLayout = 'fixed';
      table.style.marginLeft = 'auto';
      table.style.marginRight = 'auto';

      // Keep cell content tidy
      table.querySelectorAll('th,td').forEach((cell) => {
        cell.style.overflowWrap = 'anywhere';
        cell.style.wordBreak = 'break-word';
      });

      // Make any images inside cells responsive
      table.querySelectorAll('img').forEach((img) => {
        img.style.maxWidth = '100%';
        img.style.height = 'auto';
      });
    });
  });
}

const pdfDownload = async () => {
    pdfLoading.value = true;

    try {
        const elements = [].slice.call(document.getElementsByClassName('report-break'));

        if (elements.length === 0) {
            console.warn('No elements found with class "report-break"');
            pdfLoading.value = false;
            return;
        }

        const originalStates = [];

        const chartElements = [
            'topography-chart',
            'climate-precipitation-chart',
            'climate-snow-chart',
            'climate-temperature-chart',
        ]

        const graphElements = [
            'monthly-chart',
            'monthly-chart-downstream',
            'hydrologic-bar-chart'
        ]

        const legendElements = [
            'hydrologic-variability-chart-legend'
        ]

        let chartOriginalStates = await resizeS3ForPDF(elements, chartElements, 700)
        let graphOriginalStates = await resizeS3ForPDF(elements, graphElements, 500)
        let legendOriginalStates = await resizeS3ForPDF(elements, legendElements, 200)

        originalStates.push(chartOriginalStates)
        originalStates.push(legendOriginalStates)
        originalStates.push(graphOriginalStates)

        await new Promise(resolve => setTimeout(resolve, 100));

        let hasProcessedCharts = false;

        const pdfOptions = {
            filename: `${props.reportContent.overview.watershedName}_watershed_report.pdf`,
            html2canvas: {
                scale: 1.2,
                allowTaint: true,
                scrollX: 0,
                scrollY: 0,
                onclone: (clonedDoc) => {
                    resizeTablesForPDF(clonedDoc)
                }
            },
            image: {
                type: 'jpeg',
                quality: 0.9
            },
            jsPDF: {
                format: 'letter',
                orientation: 'portrait',
                compress: true
            },
            pagebreak: {
                mode: ['avoid-all', 'css', 'legacy']
            },
            margin: 16,
        };

        // Process elements one by one (safer approach)
        let worker = html2pdf().set(pdfOptions).from(elements[0]);

        if (elements.length > 1) {
            // Convert first element to PDF
            worker = worker.toPdf();

            // Add subsequent elements
            for (let i = 1; i < elements.length; i++) {
                worker = worker
                    .get('pdf')
                    .then(pdf => {
                        pdf.addPage();
                        return pdf;
                    })
                    .from(elements[i])
                    .toContainer()
                    .toCanvas()
                    .toPdf();
            }
        }

        await worker.save();

        originalStates.forEach(state => {
            state.svg.setAttribute('width', state.width);
            state.svg.setAttribute('height', state.height);
            state.svg.style.width = state.styleWidth;
            state.svg.style.height = state.styleHeight;
        });

    } catch (error) {
        console.error('PDF generation failed:', error);
        console.error('Error details:', error.message, error.stack);
    } finally {
        pdfLoading.value = false;
    }
};

</script>
