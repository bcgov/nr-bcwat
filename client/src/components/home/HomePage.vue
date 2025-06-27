<template>
    <div class="home-container">
        <div class="home-content">
            <div class="text-h2">BC Water Availability Tool</div>
            <div class="text-body1 q-mt-md">
                The BC Water Availability Tool is a point-and-click tool that helps scientists, industry explorers, 
                communities and government decision-makers to understand accurate, real-time information about water 
                resources in British Columbia.
            </div>
            <q-separator class="q-my-md" />
            <div class="text-h5">
                How to Use:
                <table>
                    <tbody>
                        <tr>
                            <td class="q-pr-md">
                                <q-icon 
                                    color="primary"
                                    name="mdi-file-document-multiple" 
                                />
                            </td>
                            <td>
                                <div class="text-h6 text-bolds">
                                    Watershed Reporting 
                                </div>
                                <p class="description">
                                    Click on a stream, lake, or river to see the watershed associated with that water feature 
                                    and generate a detailed report about it, describing water supply, demand, environmental 
                                    flow needs, and other watershed characteristics. Map markers show the location of existing 
                                    water allocations, which can be clicked on for further details.
                                </p>
                            </td>
                        </tr>
                        <tr>
                            <td class="q-pr-md">
                                <q-icon 
                                    color="primary"
                                    name="water" 
                                />
                            </td>
                            <td>
                                <div class="text-h6 text-bolds">
                                    Streamflow
                                </div>
                                <p class="description">
                                    Streamflow can be highly variable. Understanding this variability is an important part of both 
                                    managing ecosystem impacts, and ensuring a reliable water supply for use. Click on a gauge to 
                                    view an interactive report on the selected streamflow gauge, containing various data 
                                    on the gauge such as seven day flow, flow duration, flow metrics, monthly mean flow, and stage. 
                                </p>
                            </td>
                        </tr>
                        <tr>
                            <td class="q-pr-md">
                                <q-icon 
                                    color="primary"
                                    name="mdi-chart-bar" 
                                />
                            </td>
                            <td>
                                <div class="text-h6 text-bolds">
                                    Surface Water Quality
                                </div>
                                <p class="description">
                                    Report on surface water quality for waterbodies where surface water quality has been measured. 
                                    See a report with interactive charts on measurements and measured results. 
                                </p>
                            </td>
                        </tr>
                        <tr>
                            <td class="q-pr-md">
                                <q-icon 
                                    color="primary"
                                    name="mdi-water-opacity"
                                />
                            </td>
                            <td>
                                <div class="text-h6 text-bolds">
                                    Groundwater Quality
                                </div>
                                <p class="description">
                                    Report on ground water quality for wells where groundwater quality has been measured. 
                                    See a report with interactive charts on measurements and measured results. 
                                </p>
                            </td>
                        </tr>
                        <tr>
                            <td class="q-pr-md">
                                <q-icon 
                                    color="primary"
                                    name="mdi-waves-arrow-up"
                                />
                            </td>
                            <td>
                                <div class="text-h6 text-bolds">
                                    Groundwater Level
                                </div>
                                <p class="description">
                                    View details on wells where groundwater levels have been measured, such as a hydrograph on 
                                    well water depth over time, and monthly mean water levels. 
                                </p>
                            </td>
                        </tr>
                        <tr>
                            <td class="q-pr-md">
                                <q-icon 
                                    color="primary"
                                    name="mdi-weather-partly-cloudy"
                                />
                            </td>
                            <td>
                                <div class="text-h6 text-bolds">
                                    Climate
                                </div>
                                <p class="description">
                                    View interactive charts and tables for active and historical weather stations (temperature, precipitation, and snow).
                                </p>
                            </td>
                        </tr>
                    </tbody>
                </table>
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
                    The BC Water Tool is provided for public use by the Province of British Columbia
                </div>
            </div>
        </div>
    </div>
</template>

<script setup></script>

<style lang="scss">
.home-container {
    padding: 2em;
    max-height: 100vh;
    overflow-y: auto;
    width: 100%;

    .home-content {
        min-width: 500px;
        width: 60%;
    }

    .text-body1 {
        color: #4a4a4a;
    }

    .disclaimer {
        font-size: 10px;
    }

    .description {
        color: #4a4a4a;
        font-size: 16px;
        line-height: 2cap;
    }
}
</style>
