<template>
    <div class="monthly-hydrology-legend">
        <table>
            <tbody>
                <tr>
                    <td colspan="2">Existing Allocations</td>
                    <td><div class="legend-color existing"></div></td>
                </tr>
                <tr>
                    <td colspan="2">Risk Management 3</td>
                    <td><div class="legend-color rm3"></div></td>
                </tr>
                <tr>
                    <td colspan="2">Risk Management 2</td>
                    <td><div class="legend-color rm2"></div></td>
                </tr>
                <tr>
                    <td colspan="2">Risk Management 1</td>
                    <td><div class="legend-color rm1"></div></td>
                </tr>
                <tr>
                    <td>MAD</td>
                    <td>{{ props.mad.toFixed(2) }} m³/s</td>
                    
                    <td>
                        <div
                            class="legend-line"
                        >
                            <div
                                class="visual line dashed mad"
                            />
                        </div>
                    </td>
                </tr>
                <tr>
                    <td>MAD 20%</td>
                    <td>{{ (props.mad * 0.2).toFixed(2) }} m³/s</td>
                    <td>
                        <div
                            class="legend-line"
                        >
                            <div
                                class="visual line dashed mad20"
                            />
                        </div>
                    </td>
                </tr>
                <tr>
                    <td>MAD 10%</td>
                    <td>{{ (props.mad * 0.1).toFixed(2) }} m³/s</td>
                    <td>
                        <div
                            class="legend-line"
                        >
                            <div
                                class="visual line dashed mad10"
                            />
                        </div>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<script setup>
const props = defineProps({
    mad: {
        type: Number,
        default: 0,
    },
});
</script>

<style lang="scss">
.monthly-hydrology-legend {
    table {
        width: 100%;

        td {
            padding-left: 1em;
            padding-right: 1em;
        }
    }

    .legend-color {
        border: 2px solid black;
        border-radius: 3px;
        height: 1em;
        
        &.existing {
            background-color: $existing-allocations-stroke-color;
        }
        &.rm3 {
            background-color: $risk-mgmt-level-3-color;
        }
        &.rm2 {
            background-color: $risk-mgmt-level-2-color;
        }
        &.rm1 {
            background-color: $risk-mgmt-level-1-color;
        }
    }

    .legend-line {
        display: flex;
        align-items: center;
    
        .line {
            border-width: 2px;
            width: 2.5em;
 
            &.dashed {
                border-style: dashed;

                &.mad {
                    color: $mad-color;
                }
                &.mad20 {
                    color: $mad-20-color;
                }
                &.mad10 {
                    color: $mad-10-color;
                }
            }
        }
    }
}

</style>
