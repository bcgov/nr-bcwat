<template>
    <div class="q-ma-md full-height">
        <SevenDayFlow 
            :selected-point="props.activePoint"
            :y-axis-label="'Stage (m)'"
        />
    </div>
</template>

<script setup>
import SevenDayFlow from "./SevenDayFlow.vue";

const props = defineProps({
    activePoint: {
        type: Object,
        default: () => {},
    }
});
</script>
