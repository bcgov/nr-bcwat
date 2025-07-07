import { Notify } from 'quasar';

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
    const streamflowReportResponse = await fetch(`${import.meta.env.VITE_BASE_API_URL}/streamflow/stations/${id}/report`);
    return streamflowReportResponse.json();
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
    const groundwaterReportResponse = await fetch(`${import.meta.env.VITE_BASE_API_URL}/groundwater/quality/stations/${id}/report`);
    return groundwaterReportResponse.json();
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
    const groundwaterLevelReportResponse = await fetch(`${import.meta.env.VITE_BASE_API_URL}/groundwater/level/stations/${id}/report`);
    return groundwaterLevelReportResponse.json();
}

export const getSurfaceWaterReportDataById = async (id) => {
    const surfacewaterReportResponse = await fetch(`${import.meta.env.VITE_BASE_API_URL}/surface-water/stations/${id}/report`);
    return surfacewaterReportResponse.json();
}

export const getClimateReportById = async (id) => {
    const climateReportResponse = await fetch(`${import.meta.env.VITE_BASE_API_URL}/climate/stations/${id}/report`);
    return climateReportResponse.json();
}
