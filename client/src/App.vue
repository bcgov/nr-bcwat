<template>
    <div class="bcwat-container">
        <NavBar />
        <RouterView />
    </div>
</template>

<script setup>
import NavBar from "@/components/NavBar.vue";
import { RouterView, useRouter } from "vue-router";
</script>

<style lang="scss" scoped>
.bcwat-container {
    display: flex;
}
</style>
