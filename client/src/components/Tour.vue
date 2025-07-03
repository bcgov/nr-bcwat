<template>
    <div 
        class="highlight-element"
        ref="highlighter"
    />
    <div class="tour-container">
        <div 
            v-if="step > 0"
            class="tour-step"
            :style="`top: ${posY}px; left: ${posX}px;`"
        >
            <!-- <div class="notch" /> -->
            <q-card class="q-pa-md">
                <div class="tour-text">
                    {{ tourSteps[step - 1].stepContent }}
                </div>
                <div class="tour-controls">
                    <q-btn 
                        label="back"
                        flat
                        @click="step -= 1"
                    />
                    <q-btn
                        color="red"
                        label="leave tour"
                        icon="mdi-exit-to-app"
                        flat
                        @click="cancelTour"
                    />
                    <q-btn 
                        :label="step < tourSteps.length ? 'next' : 'got it!'"
                        flat
                        @click="step += 1"
                    />
                </div>
            </q-card>
        </div>
    </div>
    <q-dialog 
        v-model="tourIntro"
        persistent
        backdrop-filter="blur(2px)"
    >
        <q-card class="intro-popup q-pa-md">
            <div class="text-h5">
                Welcome to the BC Water Tool
            </div>
            <p>
                The BC Water Tool is a modular application which provides access to water related data and knowledge in support of sustainable resource management. 
                On this site you’ll find custom watershed reports for every stream, river and watershed in BC. You’ll also find monitoring 
                data from more than 50 organizations, at more than 50,000 locations across BC. 
            </p>
            <p>
                This short tour will help you find your way around. Let’s get started! 
            </p>
            <div class="col">
                <div class="row">
                    <q-btn 
                        color="primary"
                        label="No Thanks"
                        flat
                        @click="cancelTour"
                    />
                    <q-btn 
                        color="primary"
                        label="Sure"
                        @click="startTour"
                    />
                </div>
            </div>
        </q-card>
    </q-dialog>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue';

const tourSteps = [
    {
        selector: 'watershed',
        stepContent: 'Markers show locations of existing water rights. Clicking on any stream, lake, or river will generate a custom, watershed based supply and demand report.'
    },
    {
        selector: 'streamflow',
        stepContent: 'Markers show active and historical surface water quantity measurement locations.'
    },
    {
        selector: 'surface-water-quality',
        stepContent: 'Waterbodies where surface water quality has been measured.'
    },
    {
        selector: 'ground-water-quality',
        stepContent: 'Wells where ground water quality has been measured.'
    },
    {
        selector: 'ground-water-level',
        stepContent: 'Wells where groundwater levels have been measured.'
    },
    {
        selector: 'climate',
        stepContent: 'Active and historical weather stations (temperature, precipitation, and snow).'  
    },
    {
        selector: 'q-list',
        stepContent: 'Stations within the map view are listed in the sidebar. You can click them to view details on the selected point.'
    },
    {
        selector: 'search-bar-container',
        stepContent: 'Search for communities, rivers, lakes, and stations (ID, Name). You can also search by geographic coordinates (lat, long)'
    },
    {
        selector: 'help-icon',
        stepContent: 'If you would like to view the tour again, simply click this help icon!'
    }
];
const tourIntro = ref(false)
const step = ref(0);
const posY = ref(0);
const posX = ref(60);
const highlighter = ref('highlighter');

const emit = defineEmits(['show-tour'])

watch(() => step.value, (currentStep) => {
    if(currentStep <= tourSteps.length && currentStep > 0){
        setHighlightPosition(tourSteps[currentStep - 1]);
    } else {
        step.value = 0;
        emit('show-tour', false)
    }
});

onMounted(() => {
    tourIntro.value = true;
    window.addEventListener('resize', () => setHighlightPosition(step.value))
});

const setHighlightPosition = (currentStep) => {
    const currentElement = document.getElementsByClassName(currentStep.selector)[0];
    if(!currentElement) return;

    posY.value = currentElement.offsetTop > 700 ? window.innerHeight - 120 : currentElement.offsetTop;
    posX.value = currentElement.offsetWidth + 10;

    if(currentStep.selector === 'search-bar-container'){
        highlighter.value.style.left = `${window.innerWidth - (currentElement.offsetWidth + 15)}px`;
        highlighter.value.style.width = `${currentElement.offsetWidth}px`;
    } else {
        highlighter.value.style.left = `${currentElement.offsetLeft}px`;
        highlighter.value.style.width = `${currentElement.offsetWidth}px`;
    }
    highlighter.value.style.height = `${currentElement.clientHeight}px`;
    highlighter.value.style.top = `${currentElement.offsetTop}px`;
}

const startTour = () => {
    tourIntro.value = false;
    step.value += 1;
};

const cancelTour = () => {
    emit('show-tour', false);
};

</script>

<style lang="scss">
.highlight-element {
    position: absolute;
    box-shadow: 0 0 0 99999px rgba(0, 0, 0, .5);
    z-index: 99;
}

.tour-container {
    position: absolute;
    top: 0;
    left: 0;
    height: 100%;
    width: 100%;

    .tour-step {
        display: flex;
        position: relative;
        height: 150;
        width: 400px;
        z-index: 100;

        .notch {
            position: absolute;
            top: calc(50% - 10px);
            left: -10px;
            height: 20px;
            width: 20px;
            transform: rotate(45deg);
            z-index: 10;
        }

        div {
            color: white;
            background-color: $primary-light;
        }

        .tour-controls {
            display: flex;
            align-items: center;
            width: 100%;
            justify-content: space-between;
        }
    }
}

.tour-highlight {
    position: absolute;
}

.intro-popup {
    min-width: 700px;
}
</style>
