<template>
    <div class="sidebar">
        <q-list>
            <q-item
                v-for="link in links"
                :key="link.to"
                class="nav-link"
                :class="link.class"
                :active="route.path === link.url"
                active-class="active text-primary"
                clickable
                :to="link.to ? link.to : null"
                @click="link.click ? link.click() : null"
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
import { portalHandler } from '@/utils/reactor.js';
import { useRouter, useRoute } from "vue-router";

const router = useRouter();
const route = useRoute();
const emit = defineEmits(['start-tour']);

const links = [
    {
        to: "/",
        icon: "home",
        url: "/",
        label: "Dashboard",
        class: "dashboard"
    },
    {
        to: "/watershed",
        icon: "mdi-file-document-multiple",
        label: "Watershed",
        url: "/watershed",
        class: "watershed"
    },
    {
        icon: "water",
        class: "streamflow",
        label: "Streamflow",
        custom: false,
        click: () => {
            portalHandler.updateViewType('streams');
            router.push('/portal/streamflow');
        },
        url: "/portal/streamflow",
    },
    {
        icon: "mdi-chart-bar",
        label: "Surface Water Quality",
        class: "portal",
        custom: false,
        click: () => {
            portalHandler.updateViewType('surface');
            router.push('/portal/surface-water/quality');
        },
        url: "/portal/surface-water/quality",
    },
    {
        icon: "mdi-water-opacity",
        label: "Groundwater Quality",
        class: "ground-water-quality",
        click: () => {
            portalHandler.updateViewType('ground');
            router.push('/portal/groundwater/quality');
        },
        url: "/portal/groundwater/quality",
    },
    {
        icon: "mdi-waves-arrow-up",
        label: "Groundwater Level",
        class: "ground-water-level",
        click: () => {
            portalHandler.updateViewType('wells');
            router.push('/portal/groundwater/level');
        },
        url: "/portal/groundwater/level",
    },
    {
        icon: "mdi-weather-partly-cloudy",
        label: "Climate",
        class: "climate",
        click: () => {
            portalHandler.updateViewType('climate');
            router.push('/portal/climate');
        },
        url: "/portal/climate",
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
