<template>
    <div>
        <ReportChart
            v-if="sevenDayFlowChartData.length > 0"
            id="seven-day-flow-chart"
            :active-point="props.selectedPoint"
            :chart-data="sevenDayFlowChartData"
            chart-type="seven-day-flow"
            chart-name="sevenDayFlow"
            :chart-options="sevenDayFlowChartOptions"
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
const oneDay = 24 * 60 * 60 * 1000; // hours*minutes*seconds*milliseconds
const diffDays = Math.round(Math.abs((new Date(chartStart) - new Date(chartEnd)) / oneDay));

const sevenDayFlowChartData = computed(() => {
    const myData = [];
    try {
        if (props.chartData) {
            let currentDate = new Date(chartStart);
            const entryDateX = new Date(props.chartData.current[0].d);
            let day = Math.floor((entryDateX - new Date(entryDateX.getFullYear(), 0, 0)) / oneDay) - 1;

            for (let i = 0; i < diffDays; i++) {
                const entry = props.chartData.current[i]
                const ordinalDay = props.chartData.historical[day];
                const entryDate = new Date(currentDate);

                myData.push({
                    d: entryDate,
                    v : entry ? entry.v : null,
                    max: ordinalDay?.max,
                    p75: ordinalDay?.p75,
                    p50: ordinalDay?.p50,
                    p25: ordinalDay?.p25,
                    min: ordinalDay?.min,
                });

                if (entryDate.getDate() === 31 && entryDate.getMonth() === 11) {
                    day = 0;
                } else {
                    day += 1;
                }
                currentDate.setDate(currentDate.getDate() + 1);
            }
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
        endYear: years[years.length - 1],
        legend: [{
            label: 'Current',
            color: '#FFA500'
        }],
        chartColor: "#FFA500",
        yLabel: 'Flow (m³/s)',
        units: 'm³/s',
    }
});
</script>
