<template>
    <div class="bcwat-container">
        <NavBar
            @start-tour="(val) => showTour = val"
        />
        <RouterView />
        <Tour
            v-if="showTour"
            @show-tour="(val) => showTour = val"
        />
    </div>
</template>

<script setup>
import Tour from '@/components/Tour.vue';
import NavBar from "@/components/NavBar.vue";

import { RouterView } from "vue-router";
import { ref, onMounted } from 'vue';
import { version } from '../package.json';

const showTour = ref(false);

onMounted(() => {
    outputVersionNumber();
})

const outputVersionNumber = () => {
    // e.g.:
    // ▖ ▖▄▖  ▄ ▄▖▖  ▖▄▖▄▖
    // ▛▖▌▙▘▄▖▙▘▌ ▌▞▖▌▌▌▐
    // ▌▝▌▌▌  ▙▘▙▖▛ ▝▌▛▌▐
    // Running application version 4.6.1
    console.log('▖ ▖▄▖  ▄ ▄▖▖  ▖▄▖▄▖\n▛▖▌▙▘▄▖▙▘▌ ▌▞▖▌▌▌▐ \n▌▝▌▌▌  ▙▘▙▖▛ ▝▌▛▌▐ ');
    console.info(`Running application version ${version}`)
}

</script>

<style lang="scss" scoped>
body,
html {
    font-family: "BC Sans", "Inter", "Gill Sans", "Gill Sans MT", Calibri, "Trebuchet MS",
        sans-serif, "Inter";
    font-size: $base-font-size;
}
.bcwat-container {
    display: flex;
}
</style>
