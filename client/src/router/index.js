import { createRouter, createWebHistory } from "vue-router";
import { routes } from "@/utils/constants"

const router = createRouter({
    history: createWebHistory(),
    routes
});

export default router;
