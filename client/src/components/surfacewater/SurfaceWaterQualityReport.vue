<template>
    <div
        class="report-container row"
        :class="props.reportOpen ? 'open' : ''"
    >
        <div v-if="props.activePoint" class="report-sidebar">
            <div>
                <q-btn
                    class="q-mb-md"
                    color="white"
                    flat
                    label="Back to Map"
                    icon="reply"
                    dense
                    @click="() => emit('close')"
                />
            </div>
            <div class="text-h5 text-bold">
                Watershed {{ props.activePoint.name }}
            </div>
            <div class="text-h5 subtitle">ID: {{ props.activePoint.nid }}</div>
            <div class="header-grid">
                <div v-if="'net' in props.activePoint" class="col">
                    <div class="text-h6">Network</div>
                    <p>{{ props.activePoint.network }}</p>
                </div>
                <div v-if="'yr' in props.activePoint" class="col">
                    <div class="text-h6">Year Range</div>
                    <p>
                        {{ startYear }} - {{ endYear }}
                    </p>
                </div>
            </div>
            <q-separator color="white" />
            <q-list class="q-mt-sm">
                <q-item 
                    v-for="(param, idx) in chemistry.sparkline"
                    clickable 
                    :class="viewPage === idx ? 'active' : ''"
                    @click="() => (viewPage = idx)"
                >
                    <div class="text-h6">{{ param.title }} - {{ param.units }}</div>
                </q-item>
            </q-list>
            <div>
                <span class="about"
                    ><q-icon name="help" /> About this page
                    <q-tooltip>About this page content goes here.</q-tooltip>
                </span>
            </div>
            <div class="data-license cursor-pointer">Data License</div>
        </div>
        <q-tab-panels v-model="viewPage">
            <q-tab-panel
                v-for="(param, idx) in chemistry.sparkline"
                :name="idx"
            >
                <SurfaceWaterQualityChart
                    v-if="props.activePoint"
                    :selected-point="props.activePoint"
                    :data="param"
                />
            </q-tab-panel>
        </q-tab-panels>
    </div>
</template>

<script setup>
import SurfaceWaterQualityChart from '@/components/surfacewater/SurfaceWaterQualityChart.vue';
import surfaceWaterChemistry from '@/constants/surfaceWaterChemistry.json';
import { computed, onMounted, ref } from 'vue';

const emit = defineEmits(['close']);

const props = defineProps({
    reportOpen: {
        type: Boolean,
        default: false,
    },
    activePoint: {
        type: Object,
        default: () => {},
    }
});

const viewPage = ref(0);
const loading = ref(false);
const chemistry = ref([]);

const startYear = computed(() => { 
    return JSON.parse(props.activePoint.yr)[0];
})
const endYear = computed(() => { 
    return JSON.parse(props.activePoint.yr)[1];
})

onMounted(async () => {
    loading.value = true;
    await getData();
    loading.value = false;
});

const getData = async () => {
    // add API call
    chemistry.value = surfaceWaterChemistry;
}
</script>

<style lang="scss" scoped>
.data-license {
    display: flex;
    height: 100%;
    align-items: end;
    text-decoration: underline;
}

.about {
    cursor: pointer;
}

.q-item {
    &.active {
        background-color: $primary-light;
    }
}
</style>

