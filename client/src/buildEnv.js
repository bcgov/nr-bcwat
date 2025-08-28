// Only env files for build

export const buildEnv = {
    VITE_APP_MAPBOX_TOKEN: import.meta.env?.VITE_APP_MAPBOX_TOKEN ?? "",
    VITE_BASE_API_URL: import.meta.env?.VITE_BASE_API_URL ?? "http://localhost:5173/api"
};
