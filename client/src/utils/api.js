import watershed from '@/constants/watershed.json';
import streamflow from "@/constants/streamflow.json";
import climateReport from "@/constants/climateReport.json";
import climateStations from "@/constants/climateStations.json";
import groundWaterStations from "@/constants/groundWaterStations.json";
import groundwaterChemistry from "@/constants/groundWaterChemistry.json";
import groundwaterLevel from "@/constants/groundwaterLevel.json";
import groundWaterLevelStations from "@/constants/groundWaterLevelStations.json";
import surfaceWaterChemistry from '@/constants/surfaceWaterChemistry.json';
import surfaceWaterStations from "@/constants/surfaceWaterStations.json";
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
    return await mockWait(2000).then(() => watershed);
}

export const getStreamflowAllocations = async () => {
    return await mockWait(2000).then(() => streamflow);
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
            monthlyMeanFlow
        }
    });
}

export const getSurfaceWaterStations = async () => {
    return await mockWait(2000).then(() => surfaceWaterStations);
}

export const getGroundWaterStations = async () => {
    return await mockWait(2000).then(() => groundWaterStations);
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
    return await mockWait(2000).then(() => climateStations);
}

export const getGroundWaterLevelStations = async () => {
    return await mockWait(2000).then(() => groundWaterLevelStations);
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
