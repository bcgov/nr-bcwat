<template>
    <div v-if="sectionsToShow.length" class="static-report-toc">
        <div :class="props.isReport ? 'report-section-header' : ''">
            <div class="text-h4">Table of Contents</div>
        </div>
        <q-list class="table-of-contents">
            <!-- We disable header rows so they can't be hovered or clicked -->
            <q-item
                v-for="section in sectionsToShow"
                :key="section.id"
                :href="'#' + section.id"
                :disabled="section.isHeader"
                :clickable="false"
                :class="{
                    'is-hidden-touch': props.hiddenOnSmallScreens.includes(section.id),
                    'header-row': section.isHeader,
                    'divider-after': section.dividerAfter,
                    'in-group': section.inGroup,
                }"
            >
                <div class="text-h6">
                    {{ section.title }}
                </div>
            </q-item>
        </q-list>
        <q-separator class="q-my-md"/>
        <div v-if="props.reportContent.userCustomization.userNotes.length" class="report-break q-ma-md">
            <div class="text-h4">User Notes</div>
            {{ props.reportContent.userCustomization.userNotes}}
        </div>
    </div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
    sections: {
        type: Array,
        default: () => ([]),
    },

    activeId: {
        type: String,
        default: '',
    },

    // Small screens include screen tablet sized (up to 1023px according to bulma) and smaller
    hiddenOnSmallScreens: {
        type: Array,
        default: () => [],
    },

    isReport: {
        type: Boolean,
        default: false,
    },

    reportContent: {
        type: Object,
        default: () => {},
    }
});

const sectionsToShow = computed(() => {
    return props.sections.filter(section => section.id !== 'reportCover' && section.id !== 'reportToc');
});
</script>

<style lang="scss">
.report-break {
    page-break-before: always;
}

.static-report-toc {
    display: flex;
    flex-direction: column;

    .menu {
        .menu-list {
            li {
                a {
                    padding: 0.15rem 0.75rem;
                }

                &.header-row a {
                    font-size: 0.9rem;
                    text-transform: uppercase;
                }

                &.divider-after a {
                    border-bottom: 1px solid #808080;
                    padding-bottom: 0.5rem;
                    margin-bottom: 0.5rem;
                }

                &.in-group a {
                    padding-left: 3rem;
                }
            }
        }
    }

    .table-of-contents {
        font-size: 10px;
    }
}
</style>
