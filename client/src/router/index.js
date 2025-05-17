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
        },
        {
            path: "/watershed",
            name: "watershed",
            components: {
                default: () => import("@/components/watershed/Watershed.vue"),
            },
        },
        {
            path: "/streamflow",
            name: "streamflow",
            components: {
                default: () => import("@/components/streamflow/Streamflow.vue"),
            },
        },
        {
            path: "/surface-water-quality",
            name: "surface-water-quality",
            components: {
                default: () =>
                    import("@/components/surfacewater/SurfaceWater.vue"),
            },
        },
        {
            path: "/ground-water-quality",
            name: "ground-water-quality",
            components: {
                default: () =>
                    import("@/components/groundwater/GroundWater.vue"),
            },
        },
        {
            path: "/ground-water-level",
            name: "ground-water-level",
            components: {
                default: () =>
                    import(
                        "@/components/groundwater-level/GroundwaterLevel.vue"
                    ),
            },
        },
        {
            path: "/climate",
            name: "climate",
            components: {
                default: () => import("@/components/climate/ClimatePage.vue"),
            },
        },
    ],
});

export default router;
