import climateReport from "@/constants/climateReport.json";
import groundwaterChemistry from "@/constants/groundWaterChemistry.json";
import groundwaterLevel from "@/constants/groundwaterLevel.json";
import surfaceWaterChemistry from '@/constants/surfaceWaterChemistry.json';
import sevenDay from "@/constants/sevenDay.json";
import sevenDayHistorical from "@/constants/sevenDayHistorical.json";
import flowDuration from "@/constants/flowDuration.json";
import flowMetrics from "@/constants/flowMetrics.json";
import monthlyMeanFlow from "@/constants/monthlyMeanFlow.json";

const mockWait = (ms) => {
    return new Promise(resolve => {
        setTimeout(resolve, ms);
    });
} 

export const getAllWatershedStations = async () => {
    try{
        const watershedStationResponse = await fetch(`${import.meta.env.VITE_BASE_API_URL}/watershed/stations`);
        return watershedStationResponse.json();
    } catch (e) {
        Notify.create({ message: 'There was a problem fetching watershed stations.' });
    }
}

export const getStreamflowAllocations = async () => {
    try{
        const streamflowStationResponse = await fetch(`${import.meta.env.VITE_BASE_API_URL}/streamflow/stations`);
        return streamflowStationResponse.json();
    } catch (e) {
        Notify.create({ message: 'There was a problem fetching streamflow stations.' });
    }
}

/**
 * performs the API call needed to retrieve the streamflow report contents
 * for the given point via station ID. 
 * 
 * @param {string} id - the station ID to be used to fetch report data
 * @returns {object} - categorized streamflow report data
 */
export const getStreamflowReportDataById = async (id) => {
    // use id here to fetch report data. 
    return await mockWait(2000).then(() => {
        return {
            sevenDayFlow: {
                current: sevenDay,
                historical: sevenDayHistorical
            },
            flowDuration,
            flowMetrics,
            monthlyMeanFlow,
            stage: {
                current: sevenDay,
                historical: sevenDayHistorical
            }
        }
    });
}

export const getSurfaceWaterStations = async () => {
    try{
        const surfaceWaterStationResponse = await fetch(`${import.meta.env.VITE_BASE_API_URL}/surface-water/stations`);
        return surfaceWaterStationResponse.json();
    } catch (e) {
        Notify.create({ message: 'There was a problem fetching streamflow stations.' });
    }
}

export const getGroundWaterStations = async () => {
    try{
        const groundWaterStationResponse = await fetch(`${import.meta.env.VITE_BASE_API_URL}/groundwater/quality/stations`);
        return groundWaterStationResponse.json();
    } catch (e) {
        Notify.create({ message: 'There was a problem fetching streamflow stations.' });
    }
}

/**
 * performs the API call needed to retrieve the groundwater quality 
 * report contents for the given point via station ID. 
 * 
 * @param {string} id - the station ID to be used to fetch report data
 * @returns {object} - categorized groundwater quality report data
 */
export const getGroundWaterReportById = async (id) => {
    return await mockWait(2000).then(() => {
        return groundwaterChemistry;
    });
}

export const getClimateStations = async () => {
    try{
        const climateStationResponse = await fetch(`${import.meta.env.VITE_BASE_API_URL}/climate/stations`);
        return climateStationResponse.json();
    } catch (e) {
        Notify.create({ message: 'There was a problem fetching streamflow stations.' });
    }
}

export const getGroundWaterLevelStations = async () => {
    try{
        const groundWaterLevelStationResponse = await fetch(`${import.meta.env.VITE_BASE_API_URL}/groundwater/level/stations`);
        return groundWaterLevelStationResponse.json();
    } catch (e) {
        Notify.create({ message: 'There was a problem fetching streamflow stations.' });
    }
}

export const getGroundWaterLevelReportById = async (id) => {
    return await mockWait(2000).then(() => {
        return groundwaterLevel;
    });
}

export const getSurfaceWaterReportDataById = async (id) => {
    return await mockWait(2000).then(() => {
        return surfaceWaterChemistry;
    });
}

export const getClimateReportById = async (id) => {
    return await mockWait(2000).then(() => {
        return climateReport;
    });
}
