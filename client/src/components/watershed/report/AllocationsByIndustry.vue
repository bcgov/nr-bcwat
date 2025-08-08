<template>
    <div class="report-break">
        <h1 class="q-my-lg">Allocations By Industry</h1>
        <p>
            Water licences and approvals (allocations) in British Columbia are
            administered under the Water Sustainability Act. Existing, active
            water allocations in the watershed are summarized by water source,
            type, and term in the table below. On the following pages, each
            individual water allocation is listed with information on the
            specific water source and quantity, ordered by seniority.
        </p>
        <table class="allocation-industry-table">
            <tbody>
                <tr>
                    <th>Industry</th>
                    <th>Annual Volume</th>
                    <th colspan="2">Ground Water (m<sup>3</sup>)</th>
                    <th colspan="2">Surface Water (m<sup>3</sup>)</th>
                </tr>
                <tr>
                    <th colspan="2" />
                    <th>
                        <div class="box-header">
                            STUA
                            <div class="box gw-short" />
                        </div>
                    </th>
                    <th>
                        <div class="box-header">
                            Licence
                            <div class="box gw-long" />
                        </div>
                    </th>
                    <th>
                        <div class="box-header">
                            STUA
                            <div class="box sw-short" />
                        </div>
                    </th>
                    <th>
                        <div class="box-header">
                            Licence
                            <div class="box sw-long" />
                        </div>
                    </th>
                </tr>
                <tr
                    v-for="(ind, idx) in props.reportContent.allocationsByIndustry"
                    :key="idx"
                >
                    <td>{{ idx }}</td>
                    <td />
                    <td>{{ ind.gw_short }}</td>
                    <td>{{ ind.gw_long }}</td>
                    <td>{{ ind.sw_short }}</td>
                    <td>{{ ind.sw_long }}</td>
                </tr>
            </tbody>
        </table>

        <h2>Purpose Use Code Groups</h2>
        <h3>Agriculture</h3>
        <p>
            Crop Harvest, Protect & Compost, Crops: Crop Suppression, Crops:
            Flood Harvesting, Crops: Frost Protection, Greenhouse & Nursery,
            Greenhouse & Nursery: Greenhouse, Greenhouse & Nursery: Nursery,
            Irrigation: Local Provider, Irrigation: Private, Livestock & Animal,
            Livestock & Animal: Game Farm, Livestock & Animal: Kennel, Livestock
            & Animal: Stockwatering
        </p>

        <h3>Commerical</h3>
        <p>
            Bulk Shipment for Marine Transfer, Camps & Pub Facil, Camps & Pub
            Facil: Church/Com Hall, Camps & Pub Facil: Exhibition Grounds, Camps
            & Pub Facil: Institutions, Camps & Pub Facil: Non-Work Camps, Camps
            & Pub Facil: Public Facility, Camps & Pub Facil: Work Camps, Camps
            and Public Facilities, Comm. Enterprise, Comm. Enterprise: Amusement
            Park, Comm. Enterprise: Enterprise, Fish Hatchery, Fresh Water
            Bottling, Heat Exchanger, Ind'l & Comm., Ice & Snow Making, Ind'l
            Waste Mgmt: Effluent, Ind'l Waste Mgmt: Garbage Dump, Ind'l Waste
            Mgmt: Sewage Disposal, Industrial Waste Mgmt, Industrial (Well
            Drill/Transp Mgmt), Industrial-dewatering, Mineralized Water:
            Bottling & Dist, Mineralized Water: Comm. Bathing Pool, Mining:
            Hydraulic, Mining: Placer, Mining: Processing Ore, Mining: Washing
            Coal, Misc Ind'l, Misc Ind'l: Dewatering, Misc Ind'l: Fire
            Protection, Misc Ind'l: Overburden Disposal, Misc Ind'l: Sediment
            Control, N/A, Pond & Aquaculture, Processing & Mfg, Processing &
            Mfg: Fire Prevention, Processing & Mfg: Processing, Processing &
            Mfg: Wharves, Pulp Mill, Transport Mgmt: Dust Control, Transport
            Mgmt: Road Maint, Vehicle & Eqpt, Vehicle & Eqpt: Brake Cooling,
            Vehicle & Eqpt: Mine & Quarry, Vehicle & Eqpt: Truck & Eqpt Wash,
            Well Drilling/Transport Management
        </p>

        <h3>Domestic</h3>
        <p>Domestic, Incidental - Domestic</p>

        <h3>Municipal</h3>
        <p>
            Heat Exchanger, Residential, Land Improvement: General, Land
            Improvement: Ind'l for Rehab or Remed, Lwn, Fairway & Grdn, Lwn,
            Fairway & Grdn: Res L/G, Lwn, Fairway & Grdn: Watering, Swimming
            Pool, Waterworks (other than LP), Waterworks: Local Provider,
            Waterworks: Water Delivery, Waterworks: Water Sales
        </p>

        <h3>Oil & Gas</h3>
        <p>
            Industrial: Fire Suppression, Industrial: Pressure Testing,
            Industrial: Road Maintenance, Industrial: Work Camp, Oil & Gas
            Purpose: Hydraulic Fracturing, Oil & Gas Purpose: Oil Field
            Injection, Oil & Gas Purpose: Other, Oil & Gas Purpose: Well
            Drilling, Oil & Gas: Drilling, Oil & Gas: Hydraulic Fracturing (deep
            GW), Oil & Gas: Hydraulic Fracturing (non-deep GW), Oil & Gas: Oil
            field inject. (non-deep GW)
        </p>

        <h3>Other</h3>
        <p>
            Conservation: Construction Works, Conservation: Use of Water, Ice &
            Snow Making: Ice, Ice & Snow Making: Snow, Permit to Occupy Crown
            Land, River Improvement
        </p>

        <h3>Power</h3>
        <p>Cooling, Power: Commercial, Power: General, Power: Residential</p>

        <h3>Storage</h3>
        <p>
            Aquifer Storage: Non-Power, Conservation: Storage, Stream Storage:
            Non-Power, Stream Storage: Power
        </p>
        <hr class="q-my-xl" />
    </div>
</template>

<script setup>
const props = defineProps({
    reportContent: {
        type: Object,
        default: () => {},
    },
});
</script>

<style lang="scss">
.box-header {
    display: flex;
    justify-content: end;
}
.box {
    border: 1px solid black;
    border-radius: 0.3em;
    width: 20px;
    height: 20px;
    margin-left: 0.5em;

    &.gw-short {
        background-color: $color-allocations-gw-short;
    }
    &.gw-long {
        background-color: $color-allocations-gw-long;
    }
    &.sw-short {
        background-color: $color-allocations-sw-short;
    }
    &.sw-long {
        background-color: $color-allocations-sw-long;
    }
}
.allocation-industry-table {
    border-collapse: collapse;
    margin-bottom: 1em;
    width: 100%;

    tr {
        border-bottom: 1px solid $primary-font-color;
        text-align: end;

        td,
        th {
            padding: 0.5em;
        }
        :first-child {
            text-align: start;
        }

        &:first-child {
            text-align: center;
            border-bottom: unset;
        }

        &:last-child {
            border-bottom: unset;
        }
    }
}
</style>
