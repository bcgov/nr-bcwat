import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: "/",
            name: "home",
            components: {
                default: () => import("@/components/home/HomePage.vue"),
            },
            meta: {
                showMainNav: true,
            },
        },
        {
            path: "/watershed",
            name: "watershed",
            components: {
                default: () => import("@/components/watershed/Watershed.vue"),
            },
            meta: {
                showMainNav: true,
            },
        },
        {
            path: '/watershed/static-report',
            name: 'watershed-static-report',
            components: {
                default: () => import("@/components/watershed/WatershedStaticReport.vue"),
            },
            meta: {
                showMainNav: false,
            },
        },
        {
            path: "/streamflow",
            name: "streamflow",
            components: {
                default: () => import("@/components/streamflow/Streamflow.vue"),
            },
            meta: {
                showMainNav: true,
            },
        },
        {
            path: "/surface-water-quality",
            name: "surface-water-quality",
            components: {
                default: () => import("@/components/surfacewater/SurfaceWater.vue"),
            },
            meta: {
                showMainNav: true,
            },
        },
        {
            path: "/ground-water-quality",
            name: "ground-water-quality",
            components: {
                default: () => import("@/components/groundwater/GroundWaterQuality.vue"),
            },
            meta: {
                showMainNav: true,
            },
        },
        {
            path: "/ground-water-level",
            name: "ground-water-level",
            components: {
                default: () => import("@/components/groundwater-level/GroundwaterLevel.vue"),
            },
            meta: {
                showMainNav: true,
            },
        },
        {
            path: "/climate",
            name: "climate",
            components: {
                default: () => import("@/components/climate/ClimatePage.vue"),
            },
            meta: {
                showMainNav: true,
            },
        },
    ],
});

export default router;
