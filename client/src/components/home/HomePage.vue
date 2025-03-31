<script setup>
import { ref } from "vue";

defineProps({
    msg: String,
});

const count = ref(0);
</script>

<template>
    <div>MAP, probably</div>
</template>

<style scoped></style>
