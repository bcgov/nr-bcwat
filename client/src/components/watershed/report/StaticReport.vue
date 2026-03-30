<template>
<div class="static-report">
    <div class="static-report-layout">
    <div
        v-if="props.sections && props.reportContent"
        class="report-main report-content"
    >
        <div 
            v-for="section in props.sections"
            :key="section.id"
        >
            <component
                v-if="section.enabled"
                :id="section.id"
                :key="section.id"
                :is="section.sectionComponent"
                :report-content="props.reportContent"
                :diversion-information="props.diversionInformation"
                :selection-info="props.selectionInfo"
                :selected-polygon="props.selectedPolygon"
                :clicked-point="props.clickedPoint"
                :is-report="true"
                :points="props.points"
                :sections="props.sections"
                :pdf="true"
                :class="`report-section ${section.classes || ''}`"
                :wfi="props.wfi"
                @load="emit('load', section.id)"
            />
        </div>
    </div>
    </div>
</div>
</template>

<script setup>
const props = defineProps({
    /**
     * All data required by the report. This object is passed directly to the report sections.
     */
    reportContent: {
        type: Object,
        required: true,
        default: () => {},
    },
    points: {
        type: Object,
        default: () => {},
    },

    clickedPoint: {
        type: Object,
        default: () => {},
    },

    /**
     * The sections to create the report from. This array is expected to be in the following format:
     *
     *      [
     *          {
     *              title: 'Overview',
     *              id: 'overview',
     *              sectionComponent: OverviewSection,
     *          },
     *          {
     *              title: 'Introduction',
     *              id: 'introduction',
     *              sectionComponent: IntroductionSection,
     *          },
     *          [...]
     *      ]
     *
     * The sectionComponent is expected to be a Vue component.
     */
    sections: {
        type: Array,
        required: false,
        default: () => [],
    },

    /**
     * The sections to remove from the report. This is expected to be an array of section id strings.
     */
    removedSections: {
        type: Array,
        required: false,
        default: () => [],
    },

    diversionInformation: {
        type: Object,
        required: false,
        default: () => {},
    },

    selectionInfo: {
        type: Object,
        required: false,
        default: () => {},
    },

    // the user-defined polygon used to generate groundwater-specific report contents 
    selectedPolygon: {
        type: Object,
        required: false,
        default: () => {},
    },
    
    wfi: {
        type: String,
        default: '',
    }
});

const emit = defineEmits(["load"]);
</script>

<style lang="scss">
// sets the printed margin for the pdf reports
@page {
    margin: 48px;
}

.static-report-layout {
    $pdf-report-section-title-color: #695d46 !default;
    $pdf-report-section-header-background: #f2f2f2 !default;

    position: relative;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;

    // use a static width for the whole report
    width: 720px; // 8.5inch - (2 * 48px margins)
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
            margin-bottom: 0.75rem;

            .header-text {
                padding: 1rem;
                background-color: $pdf-report-section-header-background;

                .title {
                    color: $pdf-report-section-title-color;
                    font-size: 1.875rem;
                    font-weight: bold;

                    a {
                        color: inherit;
                    }
                }
                .subtitle {
                    color: $pdf-report-section-title-color;
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
}
</style>
