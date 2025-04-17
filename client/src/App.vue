<template>
    <div class="bcwat-container">
        <NavBar />
        <RouterView />
    </div>
</template>

<script setup>
import NavBar from "@/components/NavBar.vue";
import { onMounted } from "vue";
import { RouterView } from "vue-router";

onMounted(async () => {
    // Validate Connection to API
    const response = await fetch(`${import.meta.env.VITE_BASE_API_URL}/`);
    console.log(response);
});
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
