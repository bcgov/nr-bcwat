<template>
    <q-dialog
        :model-value="props.showModal"
        @update:model-value="emit('close-modal')"
    >
        <q-card
            class="customization-modal"
        >
            <q-card-section class="bg-primary text-white text-h5 header-section">
                <div>Customize your PDF report</div>
                <q-btn
                    icon="close"
                    flat
                    dense
                    @click="emit('close-modal')"
                />
            </q-card-section>
            <q-card-section>
                <div>
                    <q-input
                        v-model="userTitle"
                        hint="Report Title"
                        :maxlength="100"
                        dense
                        outlined
                    >
                        <template #counter>
                            {{ userTitle.length }} / 100
                        </template>
                    </q-input>
                </div>
                <div class="q-mt-md">
                    <q-input
                        v-model="userNotes"
                        type="textarea"
                        :maxlength="3000"
                        bottom-slots
                        hint="Notes"
                        outlined
                    >
                        <template #counter>
                            {{ userNotes.length }} / 3000
                        </template>
                    </q-input>
                </div>
                <div class="q-mt-md">
                    <div
                        v-for="section in props.reportSections.filter(el => el.enabled)"
                        :key="section.id"
                    >
                        <div
                            v-if="section.isHeader"
                            class="header-row"
                        >
                            {{ section }}
                        </div>
                        <q-checkbox
                            v-else
                            v-model="userSections"
                            :val="section.id"
                            :label="section.label"
                        />
                    </div>
                </div>
                <div class="q-mt-md">
                    <q-btn
                        label="select all"
                        @click="selectAllSections"
                    />
                    <q-btn
                        class="q-ml-md"
                        label="deselect all"
                        @click="deselectAllSections"
                    />
                </div>
                <div class="q-mt-md">
                    <q-btn
                        label="Generate Report"
                        color="primary"
                        @click="downloadReport"
                    />
                </div>
            </q-card-section>
        </q-card>
    </q-dialog>
</template>

<script setup>
import { onMounted, ref } from 'vue';

const props = defineProps({
    showModal: {
        type: Boolean,
        default: false,
    },
    reportSections: {
        type: Array,
        default: () => [],
    },
    showTitleField: {
        type: Boolean,
        default: false,
    },
    showNotesField: {
        type: Boolean,
        default: false,
    },
    modalTitle: {
        type: String,
        default: 'Customize your PDF report',
    },
    reportType: {
        type: String,
        default: 'pdf',
    },
    defaultReportTitle: {
        type: String,
        default: ''
    }
});

const userSections = ref();
const userTitle = ref("");
const userNotes = ref("");

const emit = defineEmits(['download-report', 'close-modal']);

onMounted(() => {
    emit('close-modal');
    // initially select all report sections for inclusion
    selectAllSections();
});

const downloadReport = () => {
    const userCustomization = { sections: ['reportCover', ...userSections.value] };

    if (props.showTitleField) {
        userCustomization.title = userTitle.value || props.defaultReportTitle;
    }

    if (props.showNotesField) {
        userCustomization.notes = userNotes.value;
    }

    emit('download-report', userCustomization);
};

/**
 * Select all sections to be included in the report.
 */
const selectAllSections = () => {
    userSections.value = props.reportSections.filter(s => !s.isHeader && s.enabled).map(s => s.id);
};

/**
 * Deselect all sections so that none are to be included in the report.
 */
const deselectAllSections = () => {
    userSections.value = [];
};
</script>

<style lang="scss">
.customization-modal {
    width: 30rem;

    .header-section {
        display: flex;
        justify-content: space-between;
    }
}
</style>