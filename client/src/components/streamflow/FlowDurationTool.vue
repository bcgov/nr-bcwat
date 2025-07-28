<template>
    <div>
        <div class="text-h4">Flow Duration Tool</div>
        <div
            v-if="props.chartData"
            class="flow-duration-container"
        >
            <div class="col">
                <div class="row">
                    <MonthlyFlowStatistics
                        v-if="monthDataAll.length"
                        :data="monthData"
                        :data-all="monthDataAll"
                        :dimension-filter="monthsFilter"
                        @rangeSelected="(x0, x1) => applyMonthFilter([x0, x1])"
                        @updateFilters="applyMonthFilter"
                    />
                </div>
                <div class="row">
                    <FlowDuration
                        v-if="computedCurveData.length > 0"
                        :data="computedCurveData"
                        :start-end-years="[]"
                        :start-end-months="monthsFilter"
                    />
                </div>
            </div>
            <div class="col">
                <TotalRunoff
                    v-if="yearData.length > 0"
                    :data="yearData"
                    :start-end-months="monthsFilter"
                    @month-selected="(start, end) => applyMonthFilter([start, end])"
                    @year-range-selected="(y0, y1) => onYearRangeSelected(y0, y1)"
                />
            </div>
        </div>
    </div>
</template>

<script setup>
import crossfilter from 'crossfilter2';
import reductio from 'reductio';
import MonthlyFlowStatistics from '@/components/streamflow/MonthlyFlowStatistics.vue';
import TotalRunoff from '@/components/streamflow/TotalRunoff.vue';
import FlowDuration from '@/components/streamflow/FlowDuration.vue';
import { monthAbbrList } from "@/utils/dateHelpers.js";
import { getFlowDurationByIdAndDateRange } from '@/utils/api.js';
import { computed, onMounted, ref } from 'vue';

const props = defineProps({
    chartData: {
        type: Object,
        default: () => {}
    },
});

const queryDone = ref(false);
const flowDurationData = ref(null);
const cf = ref(null);
const valuesDimension = ref(null);
const monthsDimension = ref(null);
const monthsFilter = ref([0, 11]);
const yearsDimension = ref(null);
const yearsFilter = ref([]);
const monthsGroup = ref(null);
const yearsByTotalGroup = ref(null);
const yearData = ref([]);
const yearDataAll = ref([]);
const monthData = ref([]);
const monthDataAll = ref([]);
const curveData = ref([]);
const curveDataAll = ref([]);

onMounted(() => {
    initialize();
})

// min and max years for the date picker component
const dateRange = () => {
    const min = d3.min(yearDataAll.value, d => d.key);
    const max = d3.max(yearDataAll.value, d => d.key);
    return {
        min,
        max,
    };
};

const initialize = async () => {
    if (!props.chartData) {
        return;
    }
    // initialize crossfilter and define dimensions
    cf.value = crossfilter(props.chartData);
    // fire a callback when filters change
    cf.value.onChange(cfChanged);
    // define dimensions
    valuesDimension.value = cf.value.dimension(d => d.v);
    monthsDimension.value = cf.value.dimension(d => d.m);
    yearsDimension.value = cf.value.dimension(d => d.y);

    // group by annual total
    yearsByTotalGroup.value = yearsDimension.value.group().reduceSum(d => d.v);
    // group by month
    monthsGroup.value = monthsDimension.value.group();

    // monthly min, max, median, 75%, 25%
    const monthReducer = reductio()
    .valueList(d => d.v)
    .min(true)
    .max(true)
    .median(true)
    .count(true);

    // set the month group's reducer to use reductio
    monthReducer(monthsGroup.value);

    // initialize local data
    setLocalData();
    // store the initial, unfiltered data
    yearDataAll.value = JSON.parse(JSON.stringify(yearsByTotalGroup.value.all()));
    monthDataAll.value = JSON.parse(JSON.stringify(monthsGroup.value.all()));
    // all dimension values, sorted and not yet filtered
    curveDataAll.value = JSON.parse(JSON.stringify(valuesDimension.value.top(Infinity)));
};
/**
 * callback for crossfilter change events
 * @param  {String} evType crossfilter event type
 */
const cfChanged = () => {
    // update vm as needed with the changed (filtered) datasets
    setLocalData();
    // update filter props passed to chart components
    monthsFilter.value = monthsDimension.value.currentFilter() || null;
    yearsFilter.value = yearsDimension.value.currentFilter() || null;

    // @TODO: whatever's needed for the flow duration chart
};

/**
 * update local data with current group values
 */
const setLocalData = () => {
    yearData.value = yearsByTotalGroup.value.all();
    monthData.value = monthsGroup.value.all();
    if (monthData.value.length > 0) monthData.value[0].flag = !monthData.value[0].flag;
    // all dimension values, sorted and filtered
    curveData.value = valuesDimension.value.top(Infinity);
};

const computedCurveData = computed(() => {
    let flowData = [];
    curveData.value.forEach((el, idx) => {
        flowData.push({
            v: el.v,
            exceedance: 100 * (1 - ((curveData.value.length - idx) / curveData.value.length)),
        });
    });
    return flowData;
});

const onYearRangeSelected = (y0, y1) => {
    yearsDimension.value.filter([y0, y1]);
};

/**
 * set filter on years dimension
 * pass null to clear filter
 * @param  {Array|null} years params for dimension.filter method
 */
const applyYearFilter = (years) => {
    yearsDimension.value.filter(years);
};

/**
 * set filter on months dimension
 * pass null to clear filter
 * @param  {Array|null} months params for dimension.filter method
 */
const applyMonthFilter = (months) => {
    monthsDimension.value.filter(months);
};

/**
 * reset all filters to null
 */
const resetFilters = () => {
    applyYearFilter(null);
    applyMonthFilter(null);
};
</script>

<style lang="scss">
.flow-duration-container {
    display: flex;

    .col {
        border: 1px solid aqua;
    }
}

.flow-duration-container {
    position: relative;
    display: flex;
}
</style>
