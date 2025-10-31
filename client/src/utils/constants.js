export const hydrologicWatershedColors = [
    "#1f76b4",
    "#aec7e8",
    "#2ca02c",
    "#98df8a",
    "#d62728",
    "#ff9896",
    "#9467bd",
    "#c5b0d5",
];

export const routes = [
    {
        path: "/",
        name: "home",
        component: () => import("@/components/home/HomePage.vue"),
    },
    {
        path: "/watershed",
        name: "watershed",
        component: () => import("@/components/watershed/Watershed.vue"),
    },

    {
        path: "/portal",
        name: "portal",
        redirect: '/portal/streamflow',
        props: {
            defaultViewType: 'streams'
        }
    },
    {
        path: "/streamflow",
        name: "streamflow",
        redirect: '/portal/streamflow',
        props: {
            defaultViewType: 'streams'
        }
    },
    {
        path: "/portal/streamflow",
        name: "streamflow",
        component: () => import("@/components/water-portal/WaterPortal.vue"),
        props: {
            defaultViewType: 'streams'
        }
    },
    {
        path: "/portal/groundwater/level",
        name: "groundwater-level",
        component: () => import("@/components/water-portal/WaterPortal.vue"),
        props: {
            defaultViewType: 'wells'
        }
    },
    {
        path: "/portal/groundwater/quality",
        name: "groundwater-quality",
        component: () => import("@/components/water-portal/WaterPortal.vue"),
        props: {
            defaultViewType: 'ground'
        }
    },
    {
        path: "/portal/surface-water/quality",
        name: "surface-water-quality",
        component: () => import("@/components/water-portal/WaterPortal.vue"),
        props: {
            defaultViewType: 'surface'
        }
    },
    {
        path: "/portal/climate",
        name: "climate",
        component: () => import("@/components/water-portal/WaterPortal.vue"),
        props: {
            defaultViewType: 'climate'
        }
    },
    {
        path: '/:pathMatch(.*)*', //will match everything and redirect back to root
        name: 'catchAllHome',
        redirect: '/'
    },
];
