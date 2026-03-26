<template>
    <div id="monthly-hydrology-legend" class="monthly-hydrology-legend">
        <table>
            <tbody>
                <tr>
                    <td>{{ props.isReport ? 'Existing Allocs' : 'Existing Allocations' }}</td>
                    <td><div class="legend-color existing"></div></td>
                </tr>
                <tr>
                    <td>{{ props.isReport ? 'Risk Mgmt 3' : 'Risk Management 3' }}</td>
                    <td><div class="legend-color rm3"></div></td>
                </tr>
                <tr>
                    <td>{{ props.isReport ? 'Risk Mgmt 2' : 'Risk Management 2' }}</td>
                    <td><div class="legend-color rm2"></div></td>
                </tr>
                <tr>
                    <td>{{ props.isReport ? 'Risk Mgmt 1' : 'Risk Management 1' }}</td>
                    <td><div class="legend-color rm1"></div></td>
                </tr>
            </tbody>
        </table>
        <table>
            <tbody>
                <tr>
                    <td>MAD</td>
                    <td>{{ handleDecimalPlaces(props.mad, 2) }} m³/s</td>

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
                    <td>{{ handleDecimalPlaces(props.mad * 0.2, 2) }} m³/s</td>
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
                    <td>{{ handleDecimalPlaces(props.mad * 0.1, 2) }} m³/s</td>
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
import { handleDecimalPlaces } from '@/utils/stringHelpers';
const props = defineProps({
    mad: {
        type: Number,
        default: 0,
    },
    isReport: {
        type: Boolean,
        default: false,
    }
});
</script>

<style lang="scss">
#monthly-hydrology-legend {
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
        height: 1rem;
        width: 2.5em;

        &.existing {
            border: 2px solid red;
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
        word-break: break-all;

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
