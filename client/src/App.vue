<template>
    <div class="bcwat-container kms">
        <NavBar />
        <RouterView />
    </div>
</template>

<script setup>
import NavBar from "@/components/NavBar.vue";
import { RouterView } from "vue-router";
</script>

<style lang="scss" scoped>
body,
html {
    font-family: "Inter", "Gill Sans", "Gill Sans MT", Calibri, "Trebuchet MS",
        sans-serif, "Inter" !important;
    font-size: $base-font-size;
}
.bcwat-container {
    display: flex;
}
</style>
