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
import { ref } from 'vue';

const showTour = ref(false);
</script>

<style lang="scss" scoped>
body,
html {
    font-family: "Inter", "Gill Sans", "Gill Sans MT", Calibri, "Trebuchet MS",
        sans-serif, "Inter";
    font-size: $base-font-size;
}
.bcwat-container {
    display: flex;
}
</style>
