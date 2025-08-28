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
            default: () => import("@/components/surfacewater/SurfaceWater.vue"),
        },
    },
    {
        path: "/ground-water-quality",
        name: "ground-water-quality",
        components: {
            default: () => import("@/components/groundwater/GroundWaterQuality.vue"),
        },
    },
    {
        path: "/ground-water-level",
        name: "ground-water-level",
        components: {
            default: () => import("@/components/groundwater-level/GroundwaterLevel.vue"),
        },
    },
    {
        path: "/climate",
        name: "climate",
        components: {
            default: () => import("@/components/climate/ClimatePage.vue"),
        },
    },
    {
        path: '/:pathMatch(.*)*', //will match everything and redirect back to root
        name: 'catchAllHome',
        redirect: '/'
    },
];
