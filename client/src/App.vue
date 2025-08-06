<template>
    <div class="bcwat-container">
        <NavBar 
            v-if="showMainNav()"
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

import { RouterView, useRoute } from "vue-router";
import router from '@/router/index.js';
import { computed, ref } from 'vue';

const showTour = ref(false);

const route = useRoute();
const path = computed(() => route.path)
const showMainNav = () => {
    const myPath = router.options.routes.find((route) => route.path === path.value);
    return myPath.meta.showMainNav;
};
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
