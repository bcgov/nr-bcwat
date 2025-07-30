<template>
    <div>
        <ReportChart
            v-if="streamflowStageChartData.length > 0"
            id="stage-flow-chart"
            :active-point="props.selectedPoint"
            :chart-data="streamflowStageChartData"
            chart-type="stage"
            chart-name="stage"
            :historical-chart-data="streamflowStageHistoricalChartData"
            :chart-options="streamflowStageChartOptions"
            :station-name="props.selectedPoint.name"
            yearly-type="streamflow"
        />
    </div>
</template>

<script setup>
import ReportChart from '@/components/ReportChart.vue';
import { computed } from 'vue';

const props = defineProps({
    chartData: {
        type: Object,
        default: () => {},
    },
    selectedPoint: {
        type: Object,
        default: () => {},
    }
});

const chartStart = new Date(new Date().setFullYear(new Date().getFullYear() - 1)).setDate(1);
const chartEnd = new Date(new Date().setMonth(new Date().getMonth() + 7)).setDate(0);

const streamflowStageChartData = computed(() => {
    const myData = [];
    try {
        console.log(props.chartData)
        if (props.chartData) {
            props.chartData.current.forEach((entry) => {
                const entryDate = new Date(entry.d)
                const day = Math.floor((entryDate - new Date(entryDate.getFullYear(), 0, 0)) / 1000 / 60 / 60 / 24);
                const ordinalDay = props.chartData.historical[day % 365];

                myData.push({
                    d: entryDate,
                    v: entry.v,
                    currentMax: entry.max || null,
                    currentMin: entry.min || null,
                    max: ordinalDay?.max,
                    min: ordinalDay?.min,
                    p25: ordinalDay?.p25,
                    p50: ordinalDay.p50,
                    p75: ordinalDay?.p75,
                });
            })
        } else {
            return [];
        }
    } catch (e) {
        console.error(e);
    } finally {
        console.log(myData)
        return myData;
    }
});

const streamflowStageHistoricalChartData = computed(() => {
    return [];
});

const streamflowStageChartOptions = computed(() => {
    const years = typeof props.selectedPoint.yr === 'string' ? JSON.parse(props.selectedPoint.yr) : props.selectedPoint.yr;

    return {
        name: 'Seven Day Flow',
        startYear: years[0],
        endYear: years[1],
        legend: [],
        chartColor: "#FFA500",
        yLabel: 'Flow (m³/s)',
        units: 'm³/s',
    }
});
</script>
