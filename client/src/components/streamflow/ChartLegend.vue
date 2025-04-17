<template>
<div class="legend-container">
    <div 
        v-for="legendItem in props.legendList.sort((a, b) => a.label > b.label)"
        class="legend-item"
    >
        <div 
            class="legend-color"
            :style="`background-color: ${legendItem.color}; border: 2px solid black;`"
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
    justify-content: space-around;

    .legend-item {
        display: flex;
        align-items: center;
        margin-right: 1.5rem;

        .legend-color {
            margin-right: 0.2rem;
            width: 25px;
            height: 14px;
        }   
    }
}
</style>
