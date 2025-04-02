<template>
    <div class="page-container">
        <Map />
    </div>
</template>

<script setup>
import Map from "@/components/Map.vue";
</script>

<!-- Cannot leave style tag out without breaking map for some reason -->
<style lang="scss" scoped>
.map {
    height: auto;
}
</style>
