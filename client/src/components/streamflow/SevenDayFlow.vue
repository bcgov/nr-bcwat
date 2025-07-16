<template>
    <div>
        <ReportChart
            v-if="sevenDayFlowChartData.length > 0"
            id="seven-day-flow-chart"
            :active-point="props.selectedPoint"
            :chart-data="sevenDayFlowChartData"
            chart-type="seven-day-flow"
            chart-name="sevenDayFlow"
            :historical-chart-data="sevenDayHistoricalChartData"
            :chart-options="sevenDayFlowChartOptions"
            :station-name="props.selectedPoint.name"
            yearly-type="streamflow"
        />
    </div>
</template>

<script setup>
import ReportChart from '@/components/ReportChart.vue';
import { computed, ref, onMounted } from 'vue';

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

const sevenDayFlowChartData = computed(() => {
    const myData = [];
    try {
        let i = 0;
        let currentMax = null;

        for (let d = new Date(chartStart); d <= new Date(chartEnd); d.setDate(d.getDate() + 1)) {
            const day = Math.floor((d - new Date(d.getFullYear(), 0, 0)) / 1000 / 60 / 60 / 24);
            const dataLength = props.chartData.current.length;
            const month = props.chartData.current[day % dataLength];

            if (i < props.chartData.current.length) {
                currentMax = props.chartData.current[i].v;
            } else {
                currentMax = null;
            }

            myData.push({
                d: new Date(d),
                v: month.v,
            });
            i++;
        }
    } catch (e) {
        console.error(e);
    } finally {
        return myData;
    }
});

const sevenDayHistoricalChartData = computed(() => {
    const myData = [];
    try {
        let i = 0;
        let currentMax = null;
        for (let d = new Date(chartStart); d <= new Date(chartEnd); d.setDate(d.getDate() + 1)) {
            const day = Math.floor((d - new Date(d.getFullYear(), 0, 0)) / 1000 / 60 / 60 / 24);
            const dataLength = props.chartData.historical.length;
            // note: setting to 365 will correctly set the data, we expect the data to be filled from d: 1 to d: 365 always. 
            // const dataLength = 365
            const month = props.chartData.historical[day % dataLength];

            if (i < props.chartData.historical.length) {
                currentMax = props.chartData.historical[i].v;
            } else {
                currentMax = null;
            }

            myData.push({
                d: new Date(d),
                max: month.max,
                min: month.min,
                p75: month.p75,
                p50: month.p50,
                p25: month.p25,
            });
            i++;
        }
    } catch (e) {
        console.error(e);
    } finally {
        return myData;
    }
});

const sevenDayFlowChartOptions = computed(() => {
    const years = typeof props.selectedPoint.yr === 'string' ? JSON.parse(props.selectedPoint.yr) : props.selectedPoint.yr

    return { 
        name: 'Seven Day Flow', 
        startYear: years[0], 
        endYear: years[1],
        legend: [],
        yLabel: 'Flow (m³/s)',
        units: 'm³/s',
    }
});
</script>
