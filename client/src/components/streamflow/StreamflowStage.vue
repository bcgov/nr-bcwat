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
        type: Array,
        default: () => [],
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
        let i = 0;
        for (let d = new Date(chartStart); d <= new Date(chartEnd); d.setDate(d.getDate() + 1)) {
            const day = Math.floor((d - new Date(d.getFullYear(), 0, 0)) / 1000 / 60 / 60 / 24);
            const currentDataPoint = props.chartData.current[day % 365];

            if (i < props.chartData.current.length) {
                currentMax = props.chartData.current[i].v;
            } else {
                currentMax = null;
            }

            myData.push({
                d: new Date(d),
                max: currentDataPoint.max,
                min: currentDataPoint.min,
                p75: currentDataPoint.p75,
                p50: currentDataPoint.p50,
                p25: currentDataPoint.p25,
            });
            i++;
        }
    } catch (e) {
        console.error(e);
    } finally {
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
