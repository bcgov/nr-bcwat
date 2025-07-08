<template>
    <div class="sidebar">
        <q-list>
            <q-item 
                v-for="link in links"
                :key="link.to"
                class="nav-link"
                :active="route.path === link.to"
                active-class="active text-primary"
                clickable
                :to="link.to"
            >
                <q-icon :name="link.icon" size="md" />
                {{ link.label }}
            </q-item>
        </q-list>
        <q-item 
            class="help-icon q-py-md"
            clickable
        >
            <q-icon 
                color="white"
                class="cursor-pointer"
                name="help"
                size="lg"
                @click="emit('start-tour', true)"
            />
        </q-item>
    </div>
</template>

<script setup>
import { useRoute } from "vue-router";

const route = useRoute();
const emit = defineEmits(['start-tour']);

const links = [
    {
        to: "/",
        icon: "home",
        label: "Dashboard",
        class: "dashboard"
    },
    {
        to: "/watershed",
        icon: "mdi-file-document-multiple",
        label: "Watershed",
        class: "watershed"
    },
    {
        to: "/streamflow",
        icon: "water",
        label: "Streamflow",
        class: "streamflow"
    },
    {
        to: "/surface-water-quality",
        icon: "mdi-chart-bar",
        label: "Surface Water Quality",
        class: "surface-water-quality"
    },
    {
        to: "/ground-water-quality",
        icon: "mdi-water-opacity",
        label: "Groundwater Quality",
        class: "ground-water-quality"
    },
    {
        to: "/ground-water-level",
        icon: "mdi-waves-arrow-up",
        label: "Groundwater Level",
        class: "ground-water-level"
    },
    {
        to: "/climate",
        icon: "mdi-weather-partly-cloudy",
        label: "Climate",
        class: "climate"
    },
];
</script>

<style lang="scss" scoped>
.sidebar {
    height: 100vh;
    width: $nav-width;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    background-color: $primary;
    z-index: 10;

    .nav-link {
        align-items: center;
        color: white;
        display: flex;
        flex-direction: column;
        font-size: 0.7em;
        font-weight: bold;
        text-align: center;

        &.active {
            background-color: rgba(255, 255, 255, 1);
        }
    }

    .help-icon {
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
    }
}
</style>
