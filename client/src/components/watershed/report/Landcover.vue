<template>
    <div class="q-my-lg">
        <h1>Landcover</h1>
        <p>
            The landcover characteristics influence hydrologic processes in a
            watershed. The chart below shows the landcover makeup of the Halden
            Creek watershed. These components were incorporated in the
            hydrologic model that produces the water supply estimates in this
            report, primarily influencing the evapotranspiration component of
            the water budget calculations, which represent the amount of water
            that moves directly back to the atmosphere through direct
            evaporation or transpiration by vegetation.
        </p>
        {{ Object.keys(props.reportContent.overview) }}
        <div class="landcover-container">
            <div>CHART GOES HERE</div>
            <table>
                <tbody>
                    <tr>
                        <th />
                        <th>Type</th>
                        <th>Area</th>
                        <th>% of Watershed</th>
                    </tr>
                    <tr>
                        <td>BOX</td>
                        <td>Barren</td>
                        <td>{{ props.reportContent.overview.barren }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
        <hr />
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
.landcover-container {
    display: grid;
    grid-template-columns: 50% 50%;
}
</style>
