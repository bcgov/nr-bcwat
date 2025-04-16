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
            path: "/climate",
            name: "climate",
            components: {
                default: () => import("@/components/climate/Climate.vue"),
            },
        },
        {
            path: "/surface-water-quality",
            name: "surface-water-quality",
            components: {
                default: () =>
                    import("@/components/surfacewater/SurfaceWaterQuality.vue"),
            },
        },
        {
            path: "/ground-water-quality",
            name: "ground-water-quality",
            components: {
                default: () =>
                    import("@/components/groundwater/GroundWaterQuality.vue"),
            },
        },
    ],
});

export default router;
