<template>
    <div class="text-h4">Flow Duration Tool</div>
    <div 
        v-if="chartData"
        class="flow-duration-container"
    >
        <div class="date-selector-container">
            <div class="date-selectors">
                <q-select 
                    :model-value="startYear"
                    class="selector"
                    label="Year From"
                    dense
                    :options="dataYears"
                    @update:model-value="(newval) => {
                        startYear = newval
                        onYearRangeUpdate([startYear, endYear])
                    }"
                />
                <div class="q-mx-sm">
                    -
                </div>
                <q-select 
                    :model-value="endYear"
                    class="selector q-mx-sm"
                    label="Year to"
                    dense
                    :options="dataYears"
                    @update:model-value="(newval) => {
                        endYear = newval
                        onYearRangeUpdate([startYear, endYear])
                    }"
                />
                <q-select 
                    :model-value="specifiedMonth"
                    class="selector q-mx-sm"
                    label="Month"
                    dense
                    :options="monthAbbrList"
                    data-cy="month-selector"
                    @update:model-value="(newval) => {
                        specifiedMonth = newval;
                    }"
                />
                <q-btn 
                    class="text-bold q-mx-sm"
                    label="reset dates"
                    flat
                    color="primary"
                    @click="resetDates"
                />
            </div>
        </div>
        <div class="charts-container">
            <div class="col">
                <div class="row">
                    <MonthlyFlowStatistics
                        v-if="monthDataAll && monthDataAll.length"
                        :data="monthData"
                        :data-all="monthDataAll"
                        @range-selected="applyMonthFilter"
                    />
                </div>
                <div class="row">
                    <FlowDuration
                        v-if="curveDataAll && curveDataAll.length"
                        :data="curveData"
                    />
                </div>
            </div>
            <div class="col">
                <TotalRunoff
                    v-if="chartData.length"
                    :data="yearData"
                    :data-all="yearDataAll"
                    @update-filters="applyYearFilter"
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
import flowDuration from '@/constants/flowDuration.json';
import { monthAbbrList } from "@/utils/dateHelpers.js";
import { getFlowDurationByIdAndDateRange } from '@/utils/api.js';
import { computed, onMounted, ref } from 'vue';

const monthRangeStart = ref('Jan');
const monthRangeEnd = ref('Dec');
const yearRangeStart = ref(0);
const yearRangeEnd = ref(3000);
const chartData = ref()
const specifiedMonth = ref();
const startYear = ref();
const endYear = ref();
const dataYears = ref([1914]);

// chart dimensions
const valuesDimension = ref();
const monthsDimension = ref();
const yearsDimension = ref();

// data grouping
const yearsByTotalGroup = ref();
const monthsGroup = ref();

// data
const yearData = ref();
const monthData = ref();
const curveData = ref();

// unfiltered data grouping 
const yearDataAll = ref();
const monthDataAll = ref();
const curveDataAll = ref();

// filters
const monthsFilter = ref();
const yearsFilter = ref();

// crossfilter
const cf = ref();

const props = defineProps({
    id: {
        type: Number,
        default: -1
    }
});

onMounted(async () => {
    initialize();
    yearRangeStart.value = new Date(chartData.value[0].d).getUTCFullYear();
    yearRangeEnd.value = new Date(chartData.value[chartData.value.length - 1].d).getUTCFullYear();
});

const getData = async () => {
    console.log('started loading')
    try {
        // make API call to fetch data for station
        // const data = await getFlowDurationById();
        // populate variables
        const dataWithDates = flowDuration.flow_duration_tool.map((e) => {
            const date = new Date(e.d);
            return {
                d: date,
                v: e.v,
            };
        });
        chartData.value = dataWithDates;
    } catch (ex) {
        Notify.create({ message: 'Error loading flow duration data' });
    } finally {
        console.log('loaded data.');
    }
};

const initialize = async () => {
    await getData();

    if (!chartData.value) {
        return;
    }
    // initialize crossfilter and define dimensions
    cf.value = crossfilter(chartData.value);
    // fire a callback when filters change
    cf.value.onChange(cfChanged);
    // define dimensions
    valuesDimension.value = cf.value.dimension(d => d.v);
    monthsDimension.value = cf.value.dimension(d => d.d.getMonth() + 1);
    yearsDimension.value = cf.value.dimension(d => d.d.getFullYear());

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
    // all dimension values, sorted and filtered
    curveData.value = valuesDimension.value.top(Infinity);
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
    monthsDimension.value.filter(months)
};

/**
 * reset all filters to null
 */
const resetFilters = () => {
    applyYearFilter(null);
    applyMonthFilter(null);
};

const resetDates = () => {

}
</script>

<style lang="scss">
.date-selector-container {
    display: flex;
    justify-content: end;
    
    .date-selectors {
        display: flex;
        align-items: center;

        .selector {
            width: 8rem;
        }
    }
}

.flow-duration-container {
    display: flex;
    flex-direction: column;

    .charts-container {
        display: flex;
    }
}
</style>
