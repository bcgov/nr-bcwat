import { reactive } from "vue";
import { 
    getAllWatershedLicences,
    getWaterPortalStations
} from "@/utils/api.js";

// acts as a data store which will store data while across routing actions etc. 
export const portalHandler = reactive({
    viewType: '',
    updateViewType: (viewType) => {
        portalHandler.viewType = viewType;
    }
});

export const fetchCache = reactive({
    watershedPoints: null,
    groundwaterPoints: null,
    groundwaterCaptureZones: null,
    groundwaterAquifers: null,
    waterPortal: {
        streams: null,
        surface: null,
        ground: null,
        wells: null,
        weather: null,
    },

    // fetchers to check if data already exists, otherwise fetch it
    fetchWatershedLicences: async () => {
        if(!fetchCache.watershedPoints){
            fetchCache.watershedPoints = await getAllWatershedLicences();
        }
        return fetchCache.watershedPoints;
    },
    fetchWaterPortalPoints: async (viewType) => {
        if(!fetchCache.waterPortal[viewType]){
            fetchCache.waterPortal[viewType] = await getWaterPortalStations(viewType);
        }
        return fetchCache.waterPortal[viewType];
    }
});
