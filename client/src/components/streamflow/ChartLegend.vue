<template>
<div class="legend-container">
    <div v-for="legendItem in props.legendList">
        <div 
            class="legend-color"
            :style="`background-color: ${legendItem.color};`"
        />
        <div>
            {{ legendItem.label }}
        </div>
    </div>
</div>
</template>

<script setup>
const props = defineProps({ 
    legendList: {
        type: Array,
        default: () => [],
    }
});
</script>

<style lang="scss">
.legend-container {
    display: flex;
}
</style>
