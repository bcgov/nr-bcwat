
<template>
    <h3>Total Runoff ({{ props.startEndRange[0] }} - {{ props.startEndRange[1] }})</h3>
    <div id="total-runoff-chart-container">
        <div class="svg-wrap-tr">
            <svg class="d3-chart-tr">
                <!-- d3 chart content renders here -->
            </svg>
        </div>
    </div>
</template>

<script setup>
import * as d3 from "d3";
import { onMounted, ref } from "vue";

const props = defineProps({
    data: {
        type: Array,
        default: () => [],
    },
    startEndRange: {
        type: Array,
        required: true,
    }
});

const loading = ref(false);

// chart variables
const svgWrap = ref();
const svgEl = ref();
const svg = ref();

// chart constants 
const width = 600;
const height = 300;
const margin = {
    left: 50,
    right: 50,
    top: 10,
    bottom: 50
};

onMounted(() => {
    loading.value = true;
    processData(props.data);
    initTotalRunoff();
    loading.value = false;
});

const initTotalRunoff = () => {
    if (svg.value) {
        d3.selectAll('.g-els.tr').remove();
    }

    svgWrap.value = document.querySelector('.svg-wrap-tr');
    svgEl.value = svgWrap.value.querySelector('svg');
    svg.value = d3.select(svgEl.value)
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .attr("transform", `translate(${margin.left}, ${margin.top})`);
};
</script>
