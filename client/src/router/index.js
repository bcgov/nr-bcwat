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
    ],
});

export default router;
