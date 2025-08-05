<template>
    <a :href="`#`" class="note-link" @click="scrollToNote()"
        ><sup>{{ props.noteNumber }}</sup>
        <q-tooltip max-width="30vw">
            <span class="tooltip-text-size"
                >{{ noteText }} Click for more details/links</span
            >
        </q-tooltip></a
    >
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
    noteNumber: {
        type: Number,
        default: 0,
    },
});

const noteText = computed(() => {
    return document.getElementById(`note-${props.noteNumber}`)?.innerText;
});

const scrollToNote = () => {
    document.getElementById(`note-${props.noteNumber}`).scrollIntoView({
        block: "start",
        behavior: "smooth",
        inline: "nearest",
    });
};
</script>

<style lang="scss">
.note-link {
    color: $primary;
}
.tooltip-text-size {
    font-size: 1.3em;
}
</style>
