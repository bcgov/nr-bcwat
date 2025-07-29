<template>
    <div>
        <div class="spaced-flex-row">
            <div class="text-h4">Flow Duration Tool</div>
            <div class="date-selectors">
                <q-select
                    v-model="startYear"
                    class="selector"
                    label="Year From"
                    dense
                    :options="dataYears"
                    @update:model-value="onYearRangeUpdate()"
                />
                <div class="q-mx-sm">
                    -
                </div>
                <q-select
                    v-model="endYear"
                    class="selector q-mx-sm"
                    label="Year to"
                    dense
                    :options="dataYears"
                    @update:model-value="onYearRangeUpdate()"
                />
                <q-select
                    v-model="specifiedMonth"
                    class="selector q-mx-sm"
                    label="Month"
                    dense
                    :options="monthAbbrList"
                />
                <q-btn
                    class="text-bold q-mx-sm"
                    label="reset dates"
                    flat
                    color="primary"
                    @click="resetDates()"
                />
            </div>
        </div>
        <div
            v-if="props.chartData"
            class="flow-duration-container"
        >
            <div class="col">
                <div class="row">
                    <MonthlyFlowStatistics
                        v-if="monthData.length"
                        :data="monthData"
                        :start-month="startMonth"
                        :end-month="endMonth"
                        @rangeSelected="(m0, m1) => applyMonthFilter([m0, m1])"
                    />
                </div>
                <div class="row">
                    <FlowDuration
                        v-if="curveData.length > 0"
                        :data="curveData"
                        :start-year="startYear"
                        :end-year="endYear"
                        :start-month="startMonth"
                        :end-month="endMonth"
                    />
                </div>
            </div>
            <div class="col">
                <TotalRunoff
                    v-if="yearData.length > 0"
                    :data="yearData"
                    :start-year="startYear"
                    :end-year="endYear"
                    @year-range-selected="(y0, y1) => applyYearFilter(y0, y1)"
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
import { monthAbbrList } from '@/utils/dateHelpers.js';
import { computed, onMounted, ref, watch } from 'vue';

const props = defineProps({
    chartData: {
        type: Object,
        default: () => {}
    },
});

const startYear = ref();
const endYear = ref();
const startMonth = ref(0);
const endMonth = ref(11);
const specifiedMonth = ref();

const cf = ref(null);
const valuesDimension = ref(null);
const monthsDimension = ref(null);
const monthsFilter = ref([0, 11]);
const yearsDimension = ref(null);
const yearsFilter = ref([]);
const monthsGroup = ref(null);
const yearsByTotalGroup = ref(null);
const yearData = ref([]);
const monthData = ref([]);
const curveData = ref([]);

watch(() => specifiedMonth.value, () => {
    startMonth.value = monthAbbrList.findIndex(el => el === specifiedMonth.value) + 1;
    endMonth.value = startMonth.value;
});

onMounted(() => {
    initialize();
});

const dataYears = computed(() => {
    if (yearData.value.length) {
        return [...new Set(yearData.value.map(el => el.key))];
    }
    // arbitrary year
    return [1914];
});

// min and max years for the date picker component
const dateRange = () => {
    const min = d3.min(yearData.value, d => d.key);
    const max = d3.max(yearData.value, d => d.key);
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
    curveData.value.forEach((el, idx) => {
        el.exceedance = 100 * (1 - ((curveData.value.length - idx) / curveData.value.length));
    });
};

const applyYearFilter = (y0, y1) => {
    if (!y0 || !y1) return;
    startYear.value = y0;
    endYear.value = y1;
    yearsDimension.value.filter([y0, y1]);
};

/**
 * set filter on months dimension
 * pass null to clear filter
 * @param  {Array|null} months params for dimension.filter method
 */
const applyMonthFilter = (months) => {
    monthsDimension.value.filter(months);
};

const onYearRangeUpdate = () => {
    if (startYear.value > endYear.value) {
        endYear.value = startYear.value;
    }
    applyYearFilter(startYear.value, endYear.value);
};

const resetDates = () => {
    startYear.value = null;
    endYear.value = null;
    specifiedMonth.value = '';
    yearsDimension.value.filter(null);
    applyMonthFilter(null);
};
</script>

<style lang="scss">
.flow-duration-container {
    display: flex;
}

.flow-duration-container {
    position: relative;
    display: flex;
}
</style>
