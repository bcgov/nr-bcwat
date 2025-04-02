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
            path: "/water-quality",
            name: "water-quality",
            components: {
                default: () => import("@/components/quality/WaterQuality.vue"),
            },
        },
    ],
});

export default router;
