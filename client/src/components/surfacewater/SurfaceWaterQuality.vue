<template>
    <table class="surface-water-quality-table">
        <tbody>
            <tr>
                <th class="header-text">
                    Parameter
                </th>
                <th class="header-text" /> <!-- chart column, no header -->
                <th 
                    v-for="data in dataArr"
                    class="header-text"
                >
                    {{ data }}
                </th>
            </tr>
            <tr 
                v-for="row in dataArr"
                :key="dataRow"
            >
                <td class="table-cell">
                    test
                </td>
                <td class="table-cell">
                    Chart go here
                </td>
                <td class="table-cell">
                    test
                </td>
                <td class="table-cell">
                    test
                </td>
            </tr>
        </tbody>
    </table>
</template>

<script setup>
const dataArr = [
    '1988-06-23',
    '1988-06-23'
]
</script>

<style lang="scss">
.surface-water-quality-table {
    .header-text {
        color: grey;
    }
    th, td {
        padding: 8px;
        text-align: left;
        border-bottom: 1px solid #ddd;
    }
}

.table-cell {
    min-width: 20rem;
}
</style>
