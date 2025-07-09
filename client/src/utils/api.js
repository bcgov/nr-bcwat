import { Notify } from 'quasar';
import watershedReport from '../../cypress/fixtures/watershedReport.json';

export const getAllWatershedStations = async () => {
    try{
        const watershedStationResponse = await fetch(`${import.meta.env.VITE_BASE_API_URL}/watershed/stations`);
        return watershedStationResponse.json();
    } catch (e) {
        Notify.create({ message: 'There was a problem fetching watershed stations.' });
    }
}

export const getWatershedReportByLatLng = (lngLat) => {
    try{
        // const watershedReportResponse = await fetch(`${import.meta.env.VITE_BASE_API_URL}/watershed/report/?lat=${lngLat.lat}lng=${lngLat.lng}`);
        // return watershedReportResponse.json();
        return watershedReport;
    } catch (e) {
        Notify.create({ message: 'There was a problem fetching watershed report.' });
    }
}

export const getStreamflowStations = async () => {
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
    try{
        const streamflowReportResponse = await fetch(`${import.meta.env.VITE_BASE_API_URL}/streamflow/stations/${id}/report`);
        if(streamflowReportResponse.status !== 200){
            // better errors can be thrown here, if needed/desired, but probably not necessary.
            throw 'Error';
        }
        return streamflowReportResponse.json();
    } catch (e) {
        Notify.create({ message: 'There was a problem fetching streamflow report contents.' });
        return null;
    }
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
    try{
        const groundwaterReportResponse = await fetch(`${import.meta.env.VITE_BASE_API_URL}/groundwater/quality/stations/${id}/report`);
        return groundwaterReportResponse.json();
    } catch (e) {
        Notify.create({ message: 'There was a problem fetching groundwater report contents.' });
    }
}

export const getClimateStations = async () => {
    try{
        const climateStationResponse = await fetch(`${import.meta.env.VITE_BASE_API_URL}/climate/stations`);
        return climateStationResponse.json();
    } catch (e) {
        Notify.create({ message: 'There was a problem fetching climate stations.' });
    }
}

export const getGroundWaterLevelStations = async () => {
    try{
        const groundWaterLevelStationResponse = await fetch(`${import.meta.env.VITE_BASE_API_URL}/groundwater/level/stations`);
        return groundWaterLevelStationResponse.json();
    } catch (e) {
        Notify.create({ message: 'There was a problem fetching groundwater level stations.' });
    }
}

export const getGroundWaterLevelReportById = async (id) => {
    try{
        const groundwaterLevelReportResponse = await fetch(`${import.meta.env.VITE_BASE_API_URL}/groundwater/level/stations/${id}/report`);
        if(groundwaterLevelReportResponse.status !== 200){
            // better errors can be thrown here, if needed/desired, but probably not necessary.
            throw 'Error';
        }
        return groundwaterLevelReportResponse.json();
    } catch (e) {
        Notify.create({ message: 'There was a problem fetching groundwater report for the selected station.' });
        return null;
    }
}

export const getGroundWaterLevelYearlyData = async (id, year) => {
    try{
        const groundwaterLevelReportResponse = await fetch(`${import.meta.env.VITE_BASE_API_URL}/groundwater/level/stations/${id}/report/yearly/${year}`);
        if(groundwaterLevelReportResponse.status !== 200){
            throw 'Error';
        }
    } catch (e) {
        Notify.create({ message: 'There was a problem fetching groundwater report for the selected station.' });
        return null;
    }
}

export const getSurfaceWaterReportDataById = async (id) => {
    try{
        const surfacewaterReportResponse = await fetch(`${import.meta.env.VITE_BASE_API_URL}/surface-water/stations/${id}/report`);
        return surfacewaterReportResponse.json();
    } catch (e) {
        Notify.create({ message: 'There was a problem fetching surface water report contents.' });
    }
}

export const getClimateReportById = async (id) => {
    try{
        const climateReportResponse = await fetch(`${import.meta.env.VITE_BASE_API_URL}/climate/stations/${id}/report`);
        return climateReportResponse.json();
    } catch (e) {
        Notify.create({ message: 'There was a problem fetching climate report contents.' });
    }
}
