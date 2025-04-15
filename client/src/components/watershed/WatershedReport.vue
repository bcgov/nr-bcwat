<template>
    <div class="report-container" :class="props.reportOpen ? 'open' : ''">
        <div class="spaced-flex-row">
            <h3>Watershed Report</h3>
            <q-icon
                name="mdi-close"
                size="md"
                class="cursor-pointer"
                @click="emit('close')"
            />
        </div>
        Report Content
    </div>
</template>

<script setup>
const props = defineProps({
    reportOpen: {
        type: Boolean,
        default: false,
    },
});

const emit = defineEmits(["close"]);
</script>

<style lang="scss" scoped>
.spaced-flex-row {
    padding: 1em;
}
</style>
