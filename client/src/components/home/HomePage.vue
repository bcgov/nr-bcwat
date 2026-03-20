<template>
    <div class="home-container">
        <div id="home-header" class="q-pa-md">
            <q-img
                src="/bclogo_white.png"
                fit="scale-down"
                width="200px"
            />
            <div class="text-h3 q-ml-lg">BC Water Availability Tool</div>
        </div>
        <div class="home-content">
            <div class="width-limit">
                <div class="text-body1">
                    The BC Water Availability Tool is a point-and-click tool that helps scientists, industry explorers,
                    communities and government decision-makers to understand accurate, real-time information about water
                    resources in British Columbia.
                </div>
                <q-separator class="q-my-md" />
                <div class="text-h6">
                    How to Use:
                    <q-list
                        class="home-page-links"
                    >
                        <q-item
                            clickable
                            to="/watershed"
                        >
                            <q-item-section avatar>
                                <q-icon
                                    class="q-mr-md"
                                    color="primary"
                                    name="mdi-file-document-multiple"
                                    size="md"
                                />
                            </q-item-section>
                            <q-item-section>
                                <div>
                                    Watershed Reporting
                                </div>
                                <div class="text-body1">
                                    Click on a stream, lake, or river to see the watershed associated with that water feature
                                    and generate a detailed report about it, describing water supply, demand, environmental
                                    flow needs, and other watershed characteristics. Map markers show the location of existing
                                    water allocations, which can be clicked on for further details.
                                </div>
                            </q-item-section>
                        </q-item>
                        <q-separator class="q-my-sm"/>
                        <q-item
                            clickable
                            @click="() => {
                                portalHandler.updateViewType('streams');
                                router.push('/portal/streamflow');
                            }"
                        >
                            <q-item-section avatar>
                                <q-icon
                                    class="q-mr-md"
                                    color="primary"
                                    name="water"
                                    size="md"
                                />
                            </q-item-section>
                            <q-item-section>
                                <div>
                                    Streamflow
                                </div>
                                <div class="text-body1">
                                    Streamflow can be highly variable. Understanding this variability is an important part of both
                                    managing ecosystem impacts, and ensuring a reliable water supply for use. Click on a gauge to
                                    view an interactive report on the selected streamflow gauge, containing various data
                                    on the gauge such as seven day flow, flow duration, flow metrics, monthly mean flow, and stage.
                                </div>
                            </q-item-section>
                        </q-item>
                        <q-separator class="q-my-sm"/>
                        <q-item
                            clickable
                            @click="() => {
                                portalHandler.updateViewType('surface');
                                router.push('/portal/surface-water/quality');
                            }"
                        >
                            <q-item-section avatar>
                                <q-icon
                                    class="q-mr-md"
                                    color="primary"
                                    name="mdi-chart-bar"
                                    size="md"
                                />
                            </q-item-section>
                            <q-item-section>
                                <div>
                                    Surface Water Quality
                                </div>
                                <div class="text-body1">
                                    Report on surface water quality for waterbodies where surface water quality has been measured.
                                    See a report with interactive charts on measurements and measured results.
                                </div>
                            </q-item-section>
                        </q-item>
                        <q-separator class="q-my-sm"/>
                        <q-item
                            clickable
                            @click="() => {
                                portalHandler.updateViewType('ground');
                                router.push('/portal/groundwater/quality');
                            }"
                        >
                            <q-item-section avatar>
                                <q-icon
                                    class="q-mr-md"
                                    color="primary"
                                    name="mdi-water-opacity"
                                    size="md"
                                />
                            </q-item-section>
                            <q-item-section>
                                <div>
                                    Groundwater Quality
                                </div>
                                <div class="text-body1">
                                    Click on a point to report on ground water quality for wells where groundwater quality has been measured.
                                    View a report with interactive charts on measurements and measured water quality results.
                                </div>
                            </q-item-section>
                        </q-item>
                        <q-separator class="q-my-sm"/>
                        <q-item
                            clickable
                            @click="() => {
                                portalHandler.updateViewType('wells');
                                router.push('/portal/groundwater/level');
                            }"
                        >
                            <q-item-section avatar>
                                <q-icon
                                    class="q-mr-md"
                                    color="primary"
                                    name="mdi-waves-arrow-up"
                                    size="md"
                                />
                            </q-item-section>
                            <q-item-section>
                                <div>
                                    Groundwater Level
                                </div>
                                <div class="text-body1">
                                    Click on a point to view details on wells where groundwater levels have been measured, such as a hydrograph on
                                    well water depth over time, and monthly mean water levels.
                                </div>
                            </q-item-section>
                        </q-item>
                        <q-separator class="q-my-sm"/>
                        <q-item
                            clickable
                            @click="() => {
                                portalHandler.updateViewType('climate');
                                router.push('/portal/climate');
                            }"
                        >
                            <q-item-section avatar>
                                <q-icon
                                    class="q-mr-md"
                                    color="primary"
                                    name="mdi-weather-partly-cloudy"
                                    size="md"
                                />
                            </q-item-section>
                            <q-item-section>
                                <div>
                                    Climate
                                </div>
                                <div class="text-body1">
                                    Click on a point to view interactive charts and tables for active and historical weather stations (temperature, precipitation, and snow).
                                </div>
                            </q-item-section>
                        </q-item>
                    </q-list>
                </div>
                <q-separator class="q-my-md" />
                <div class="disclaimer">
                    <div class="text-bold">Disclaimer</div>
                    It is the responsibility of all persons who use this site to independently confirm the accuracy of the data,
                    information, or results obtained through the use of BCWAT, should it be necessary for their purpose. No warranty
                    of quality, accuracy, or completeness of any information, data or product from these web pages is made. No
                    liability or blame for loss or damages incurred by any person or business entity based on the use of BCWAT is
                    accepted. It is provided 'AS IS' without warranty or condition of any nature. BCWAT carries no guarantee of any
                    kind, expressed or implied. Use of this site will constitute your acceptance of these terms and conditions.
                </div>
                <q-separator class="q-my-md" />
                <div>
                    <div class="description">
                        <!-- add bc gov logo here -->
                        <q-img
                            src="/bclogo.png"
                            width="200px"
                        />
                        The BC Water Tool is provided for public use by the Province of British Columbia
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { portalHandler } from '@/utils/reactor.js';
import { onMounted } from 'vue';

onMounted(() => {
    const navLink = document.getElementsByClassName('nav-link');
    if (navLink.length > 0) {
        const homeHeader = document.getElementById('home-header');
        homeHeader.style.height = `${navLink[0].offsetHeight}px`;
    }
});

const router = useRouter();
</script>

<style lang="scss">
.home-container {
    display: flex;
    flex-direction: column;
    max-height: 100vh;

    #home-header {
        align-items: center;
        background-color: $primary;
        color: white;
        display: flex;
    }

    .home-content {
        min-width: 500px;
        overflow-y: auto;
        padding: 2em;

        .width-limit {
            width: 60%;
        }
    }

    .text-body1 {
        color: #4a4a4a;
    }

    .disclaimer {
        font-size: 10px;
    }
}
</style>
