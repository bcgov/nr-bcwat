<template lang="html">
    <div class="hydrologic-variability-chart-legend" ref="el">
        <p class="q-mb-none">Monthly flow percentile</p>
        <div class="legend-svg-wrap">
            <svg>
                <rect
                    class="bar-outer"
                    :x="margin.left"
                    :y="margin.top"
                    :width="barWidth"
                    :height="height"
                />
                <rect
                    class="bar-inner"
                    :x="margin.left"
                    :y="margin.top + 0.2 * outerHeight"
                    :width="barWidth"
                    :height="innerHeight"
                />
                <!-- add a label for each percentile -->
                <g v-for="percentile in items" :key="percentile.label">
                    <line
                        class="percentile-line"
                        :y1="margin.top + (outerHeight * percentile.y) / 100"
                        :y2="margin.top + (outerHeight * percentile.y) / 100"
                        :x1="margin.left"
                        :x2="width - 30"
                    />
                    <text
                        class="percentile-label"
                        :y="margin.top + (outerHeight * percentile.y) / 100"
                        :x="width - 30 + 5"
                        alignment-baseline="central"
                        v-text="percentile.label"
                    />
                </g>
            </svg>
        </div>
    </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";

const items = [
    { label: "90th", y: 0 },
    { label: "75th", y: 20 },
    { label: "25th", y: 80 },
    { label: "10th", y: 100 },
];
const width = ref(100);
const height = ref(100);
const barWidth = 25;
const margin = {
    top: 10,
    right: 0,
    bottom: 10,
    left: 0,
};

const el = ref(null);

const outerHeight = computed(() => {
    return height.value;
});

const innerHeight = computed(() => {
    const difference = (items[2].y - items[1].y) / 100;
    return difference * outerHeight.value;
});

onMounted(() => {
    const resizeObserver = new ResizeObserver((entries) => {
        const { width, height } = entries[0].contentRect;
        if (width && height) {
            init();
        }
    });
    resizeObserver.observe(el.value);
});

const init = () => {
    const svgWrap = el.value.querySelector(".legend-svg-wrap");
    width.value = svgWrap.clientWidth - margin.left - margin.right;
    height.value = svgWrap.clientHeight - margin.top - margin.bottom; // adjust for the svg title
};
</script>

<style lang="scss">
.hydrologic-variability-chart-legend {
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 5px;
    margin: 1em 0 1em 0;
    max-width: 130px;
    padding: 0.5em;
    .legend-svg-wrap {
        > svg {
            height: 100%;
            width: 100%;

            rect,
            line {
                shape-rendering: crispEdges;
            }

            .bar-inner {
                fill: $color-hydrovar-legend-inner;
            }

            .bar-outer {
                fill: $color-hydrovar-legend-outer;
            }

            .percentile-line {
                stroke-width: 1px;
                stroke: $grey-light;
            }

            .percentile-label {
                font-size: 12px;
                fill: currentColor;
            }
        }
    }
}
</style>
