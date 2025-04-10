<template>
    <div class="sidebar">
        <router-link
            v-for="link in links"
            :key="link.to"
            :to="link.to"
            class="nav-link"
            :class="route.path === link.to ? 'active' : ''"
        >
            <q-icon :name="link.icon" size="md" class="q-mr-md" />
            {{ link.label }}
        </router-link>
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
        icon: "water",
        label: "Watershed",
    },
    {
        to: "/streamflow",
        icon: "poll",
        label: "Streamflow",
    },
    {
        to: "/climate",
        icon: "looks",
        label: "Climate",
    },
    {
        to: "/water-quality",
        icon: "mdi-water",
        label: "Water Quality",
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

    .nav-link {
        border: 1px solid transparent;
        color: white;
        font-weight: bold;
        padding: 1em;
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
}
</style>
