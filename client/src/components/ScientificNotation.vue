<!-- This component displays numbers in scientific notation if they are greater than 9999, formatted nicely like 1.67x10^7 -->
<template>
    <span
        v-if="props.num > 9999"
        :title="props.num"
    >
        {{ props.num.toExponential(2).substring(0, 4) }}x10<sup>{{ props.num.toExponential(2).substring(6, props.num.toExponential(2).length) }}</sup>
    </span>
    <span
        v-else
        :title="props.num"
    >
        {{ props.num.toFixed(2) }}
    </span>
</template>
<script setup>
const props = defineProps({
    num: {
        type: Number,
        default: 0,
    },
});
</script>
