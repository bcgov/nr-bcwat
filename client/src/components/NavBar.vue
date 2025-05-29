<template>
    <div class="sidebar">
        <router-link
            v-for="link in links"
            :key="link.to"
            :to="link.to"
            class="nav-link"
            :class="route.path === link.to ? 'active' : ''"
        >
            <q-icon :name="link.icon" size="md" />
            {{ link.label }}
        </router-link>
        <q-space />
        <div class="help-icon">
            <q-icon 
                color="white"
                class="cursor-pointer"
                name="help"
                size="lg"
            />
        </div>
    </div>
</template>

<script setup>
import { useRoute } from "vue-router";

const route = useRoute();

const links = [
    {
        to: "/",
        icon: "home",
        label: "Dashboard",
    },
    {
        to: "/watershed",
        icon: "mdi-file-document-multiple",
        label: "Watershed",
    },
    {
        to: "/streamflow",
        icon: "water",
        label: "Streamflow",
    },
    {
        to: "/surface-water-quality",
        icon: "mdi-chart-bar",
        label: "Surface Water Quality",
    },
    {
        to: "/ground-water-quality",
        icon: "mdi-water-opacity",
        label: "Groundwater Quality",
    },
    {
        to: "/ground-water-level",
        icon: "mdi-waves-arrow-up",
        label: "Groundwater Level",
    },
    {
        to: "/climate",
        icon: "mdi-weather-partly-cloudy",
        label: "Climate",
    },
];
</script>

<style lang="scss" scoped>
.sidebar {
    height: 100vh;
    width: $nav-width;
    display: flex;
    flex-direction: column;
    background-color: $navbar;
    z-index: 10;

    .nav-link {
        align-items: center;
        border: 1px solid transparent;
        color: white;
        display: flex;
        flex-direction: column;
        font-size: 0.7em;
        font-weight: bold;
        padding: 1em;
        text-align: center;
        width: $nav-width;

        &:hover {
            background-color: darkgrey;
            border: 1px solid white;
        }

        &.active {
            background-color: grey;
            border: 1px solid white;
        }
    }

    .help-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 1rem;
    }
}
</style>
