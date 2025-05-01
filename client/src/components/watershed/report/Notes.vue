<template>
    <div class="notes-section">
        <h1 class="q-my-lg">Notes</h1>
        <ol>
            <li id="note-1" class="note">
                <div class="note-text">
                    <p>For more information please contact Frontcounter BC</p>
                    <ul class="no-bullets">
                        <li>
                            <q-icon name="email" class="pr-1" />
                            <div class="list-item-text">
                                Email:
                                <a href="mailto:frontcounterbc@gov.bc.ca">
                                    frontcounterbc@gov.bc.ca
                                </a>
                            </div>
                        </li>
                        <li>
                            <q-icon name="phone" class="pr-1" />
                            <div class="list-item-text">
                                Toll Free: 1-877-855-3222
                            </div>
                        </li>
                        <li>
                            <q-icon name="phone" class="pr-1" />
                            <div class="list-item-text">
                                Outside North America: ++1-778-372-0729
                            </div>
                        </li>
                        <li>
                            <q-icon name="mdi-open-in-new" class="pr-1" />
                            <div class="list-item-text">
                                On the web:
                                <a
                                    target="_blank"
                                    href="http://www.frontcounterbc.gov.bc.ca/"
                                >
                                    http://www.frontcounterbc.gov.bc.ca/
                                </a>
                            </div>
                        </li>
                    </ul>
                </div>
            </li>

            <li id="note-2" class="note">
                <div class="note-text">
                    <p>
                        The downstream watershed is defined as the mouth of the
                        queried stream. If that downstream watershed's area is
                        within 15% of the queried drainage area, then the
                        watershed at the mouth of the next downstream stream is
                        chosen as the downstream watershed. For information
                        further downstream, please generate an additional report
                        at a location of interest. Predictions for small
                        watersheds (generally smaller than 50 sq. km.) may be
                        less accurate due to the lack of hydrometric data
                        available for watersheds of this size. These small
                        watersheds are highly sensitive to localized weather
                        events, resulting in highly variable conditions both
                        within and between years.
                    </p>
                </div>
            </li>

            <li id="note-3" class="note">
                <div class="note-text">
                    <p>
                        The hydrologic model employed a water balance approach
                        to estimate runoff in ungauged basins. The model was
                        calibrated using stream flow measurements from the Water
                        Survey of Canada, and validated using a leave-one-out
                        cross-validation. The model used
                        {{ modelInformation.numWatersheds }} watersheds with
                        hydrometric gauges and included detailed information on
                        climate, evapotranspiration, topography, vegetation and
                        land cover. Error metrics calculated for mean annual
                        discharge for the entire model domain are: Mean error =
                        {{ modelInformation.meanError }}%, Median Error =
                        {{ modelInformation.medianError }}%, Mean Absolute Error
                        = {{ modelInformation.meanAbsoluteError }}%, Watersheds
                        within +/- 20% =
                        {{ modelInformation.watershedsWithin20Percent }}%. This
                        model was subsequently adjusted to remove residual error
                        at both the annual and monthly scales, for the
                        watersheds covered by the WAT. To generate the weekly
                        estimates of flow variability which are used in the BC
                        WAT, flow distributions from a set of gauged hydrometric
                        stations were transposed to ungauged basins. For further
                        information on this process please contact us at
                        <a
                            target="_blank"
                            href="https://foundryspatialsm.atlassian.net/servicedesk/customer/portal/12"
                        >
                            https://foundryspatialsm.atlassian.net/servicedesk/customer/portal/12 </a
                        >.
                    </p>
                </div>
            </li>

            <li id="note-4" class="note">
                <div class="note-text">
                    <p>
                        Information on water reserves and restrictions can be
                        found at the following links:
                    </p>
                    <p>
                        Water Reserves:
                        <br />
                        <a
                            target="_blank"
                            href="https://www2.gov.bc.ca/gov/content/environment/air-land-water/water/water-licensing-rights/water-reservations"
                        >
                            https://www2.gov.bc.ca/gov/content/environment/air-land-water/water/water-licensing-rights/water-reservations
                        </a>
                    </p>
                    <p>
                        Water Allocation Notations:
                        <br />
                        <a
                            target="_blank"
                            href="https://www2.gov.bc.ca/gov/content/environment/air-land-water/water/water-licensing-rights/water-allocation-notations"
                        >
                            https://www2.gov.bc.ca/gov/content/environment/air-land-water/water/water-licensing-rights/water-allocation-notations
                        </a>
                    </p>
                </div>
            </li>

            <li id="note-5" class="note">
                <div class="note-text">
                    <p>
                        <i>Ptolemy, 2015.</i>
                    </p>
                </div>
            </li>

            <li id="note-6" class="note">
                <div class="note-text">
                    <p>
                        The hydrology model governing gross water supply is
                        described in Chapman et al, 2018. A document describing
                        how this model was enhanced and extended to support the
                        calculations in this report, can be provided by
                        submitting a request at
                        <a
                            target="_blank"
                            href="https://foundryspatialsm.atlassian.net/servicedesk/customer/portal/12"
                        >
                            https://foundryspatialsm.atlassian.net/servicedesk/customer/portal/12 </a
                        >.
                    </p>
                </div>
            </li>

            <li id="note-7" class="note">
                <div class="note-text">
                    <a
                        target="_blank"
                        href="https://www2.gov.bc.ca/gov/content/environment/air-land-water/water/water-licensing-rights/water-policies/environmental-flow-needs"
                    >
                        https://www2.gov.bc.ca/gov/content/environment/air-land-water/water/water-licensing-rights/water-policies/environmental-flow-needs
                    </a>
                </div>
            </li>

            <li id="note-8" class="note">
                <div class="note-text">
                    Water Rights Licences imported June 13, 2023 from
                    <a
                        href="https://catalogue.data.gov.bc.ca/dataset/water-rights-licences-public"
                        >https://catalogue.data.gov.bc.ca/dataset/water-rights-licences-public</a
                    >
                </div>
            </li>

            <li id="note-9" class="note">
                <div class="note-text">
                    Water Rights Applications imported June 13, 2023 from
                    <a
                        href="https://catalogue.data.gov.bc.ca/dataset/water-rights-applications-public"
                        >https://catalogue.data.gov.bc.ca/dataset/water-rights-applications-public</a
                    >
                </div>
            </li>

            <li id="note-10" class="note">
                <div class="note-text">
                    BCER Short term Approvals imported August 22, 2023 from
                    <a
                        target="_blank"
                        href="https://data-bcogc.opendata.arcgis.com/datasets/fcc52c0cfb3e4bffb20518880ec36fd0_0"
                    >
                        https://data-bcogc.opendata.arcgis.com/datasets/fcc52c0cfb3e4bffb20518880ec36fd0_0
                    </a>
                </div>
            </li>

            <li id="note-11" class="note">
                <div class="note-text">
                    Province of BC Water Approval Points imported June 13, 2023
                    from
                    <a
                        target="_blank"
                        href="https://catalogue.data.gov.bc.ca/dataset/water-approval-points"
                    >
                        https://catalogue.data.gov.bc.ca/dataset/water-approval-points
                    </a>
                </div>
            </li>

            <li id="note-12" class="note">
                <div class="note-text">
                    Water presented as "Potential Allocations" within this
                    report is determined in consideration of the Decisions on
                    Applications for Water Diversion and Use in the Blueberry,
                    Upper Beatton, and Lower Sikanni Chief Watersheds: Phase Two
                </div>
            </li>

            <li id="note-13" class="note">
                <div class="note-text">
                    <a
                        href="https://www2.gov.bc.ca/gov/content/environment/air-land-water/water/laws-rules/water-sustainability-act"
                        >https://www2.gov.bc.ca/gov/content/environment/air-land-water/water/laws-rules/water-sustainability-act</a
                    >
                </div>
            </li>

            <li id="note-14" class="note">
                <div class="note-text">
                    Water Licence Flag Descriptions:
                    <ul>
                        <li>
                            D : Multiple PODs for PUC, qty at each are known,
                            PODs on different sources
                        </li>
                        <li>
                            M : Max licenced demand for purpose, multiple PODs,
                            qty at each POD unknown
                        </li>
                        <li>
                            P : Multiple PODs for PUC, qty at each are known,
                            PODs on same source
                        </li>
                        <li>T : Total demand for PUC, one POD</li>
                        <li>
                            N : Licence volumes not used in annual or monthly
                            allocation calculations
                        </li>
                    </ul>
                </div>
            </li>

            <li id="note-15" class="note">
                <div class="note-text">
                    <p>
                        The land cover data for BC was sourced from the
                        2000-Land Cover Vector product, produced and distributed
                        by Natural Resources Canada. For Alaska, the land cover
                        data was sourced from the 2001 national land cover
                        database for the United States. Where the previous two
                        sources were missing data, the land cover data was
                        infilled with the 2013 North American Land Change
                        Monitoring System Land Cover.
                    </p>
                    <p class="half-margin">BC: <i>Geobase, 2009.</i></p>
                    <p class="half-margin">AK: <i>Homer et al, 2004.</i></p>
                    <p class="half-margin">Infill: <i>CEC, 2013.</i></p>
                </div>
            </li>

            <li id="note-16" class="note">
                <div class="note-text">
                    <p>
                        ClimateWNA v{{ climateChartInformation.cwnaVersion }}
                        <i>(Wang et al, 2012)</i>
                        was used to produce estimates for the
                        {{ climateChartInformation.cwnaDriverYears }} climate
                        normal as well as
                        {{ climateChartInformation.futureDriverYears }} future
                        climate scenarios. The three future climate scenarios
                        used are the
                        {{ climateChartInformation.futureScenario1 }},
                        {{ climateChartInformation.futureScenario2 }}, and
                        {{ climateChartInformation.futureScenario3 }}. These
                        represent a range of generally hot/dry, warm/very wet,
                        and moderately warm/wet future climates, respectively.
                    </p>
                </div>
            </li>

            <li id="note-17" class="note">
                <div class="note-text">
                    <p>
                        <i>Pike and Wilford, 2013.</i>
                    </p>
                </div>
            </li>

            <li id="note-19" class="note">
                <div class="note-text">
                    <p>
                        FLNRORD Water Approval Points imported
                        {{ importDates.wls_water_approvals }} from
                        <a
                            target="_blank"
                            href="https://catalogue.data.gov.bc.ca/dataset/water-approval-points"
                            >https://catalogue.data.gov.bc.ca/dataset/water-approval-points</a
                        >
                    </p>
                </div>
            </li>
        </ol>
        <hr />
    </div>
</template>

<script setup>
import {
    CLIMATE_CHART,
    FS_HYDROLOGY_MODEL,
} from "@/constants/model-information.js";
import { computed } from "vue";
import dayjs from "dayjs";

const props = defineProps({
    reportContent: {
        type: Object,
        default: () => {},
    },
});

const importDates = computed(() => {
    const dates = {};

    props.reportContent.licenceImportDates.forEach((date) => {
        dates[date.dataset] = dayjs(date.import_date).format("MMMM DD, YYYY");
    });

    return dates;
});

const modelInformation = computed(() => {
    return FS_HYDROLOGY_MODEL;
});

const climateChartInformation = computed(() => {
    return CLIMATE_CHART;
});
</script>

<style lang="scss">
.notes-section {
    * {
        margin: 0;
        padding: 0;
    }
    font-size: 1rem;
    line-height: 1.25rem;

    *:last-child {
        margin-bottom: 0 !important;
    }

    > ol {
        list-style: none;
        counter-reset: item;
    }

    .note {
        margin: 1rem 0;
        counter-increment: item;
        display: flex;
        flex-direction: row;
        page-break-inside: avoid;

        &::before {
            margin-right: 0.5em;
            color: $primary-light;
            content: counter(item) ". ";
        }

        .note-text {
            flex: 1;
            flex-direction: column;
            @media screen and (max-width: 1408px) {
                max-width: 85vw;
            }

            ul,
            ol {
                margin-bottom: 1em;
            }

            li {
                list-style-type: circle;
                margin: 0 0 0.5em 2em;
            }

            ul.no-bullets li {
                list-style-type: none;
                margin-left: 0;
                display: flex;
                flex-direction: row;

                .icon {
                    margin-right: 0.4em;
                    margin-top: 0.25em;
                }
            }

            .b-table {
                max-width: 50em;
            }

            a {
                word-break: break-all;
            }

            p {
                margin-top: 0;

                &.half-margin {
                    margin-bottom: 0.5em;
                }
            }
        }
    }
}
</style>
