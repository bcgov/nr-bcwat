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
            path: "/reports",
            name: "reports",
            components: {
                default: () => import("@/components/watershed/HelloWorld.vue"),
            },
        },
    ],
});

export default router;
