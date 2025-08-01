import { Notify } from 'quasar';
import { env } from '@/env';
import cache from './cache';


const requestWithErrorCatch = async (url, fetchType) => {
    try{
        const response = await fetch(url);
        if(response.status === 404){
            if(fetchType === 'report') throw { message: 'No report data for the selected point. Try selecting another point.' };
            throw { message: 'No data found.' }
        }
        if(response.status === 500){
            if(fetchType === 'report') throw { message: 'There was a problem getting report data. Please try again later. ' };
            throw { message: 'There was a problem fetching data. Please try again later.' };
        }
        return response.json();
    }
    catch (e) {
        Notify.create({ message: e.message });
    }
}

export const getAllWatershedLicences = async () => {
    const cachedWatershedLicenses = cache.getData('watershedLicenses')
    if (cachedWatershedLicenses) {
        return cachedWatershedLicenses
    } else {
        const watershedLicenses = await requestWithErrorCatch(`${env.VITE_BASE_API_URL}/watershed/licences`);
        cache.setData('watershedLicenses', watershedLicenses)
        return watershedLicenses
    }
}

export const getWatershedBySearch = async (wfi) => {
    return await requestWithErrorCatch(`${env.VITE_BASE_API_URL}/watershed/search?wfi=${wfi}`)
}

export const getWatershedByWFI = async (wfi) => {
    return await requestWithErrorCatch(`${env.VITE_BASE_API_URL}/watershed/${wfi}`)
}

export const getWatershedLicenceBySearch = async (licence_no) => {
    return await requestWithErrorCatch(`${env.VITE_BASE_API_URL}/watershed/licences/search?licence_no=${licence_no}`)
}

export const getWatershedByLatLng = async (lngLat) => {
    return await requestWithErrorCatch(`${env.VITE_BASE_API_URL}/watershed/?lat=${lngLat.lat}&lng=${lngLat.lng}`);
}

export const getWatershedReportByWFI = async (wfi) => {
    return await requestWithErrorCatch (`${env.VITE_BASE_API_URL}/watershed/${wfi}/report`);
}

export const getStreamflowStations = async () => {
    const cachedStreamflowStations = cache.getData('streamflowStations')
    if (cachedStreamflowStations) {
        return cachedStreamflowStations
    } else {
        const streamflowStations = await requestWithErrorCatch(`${env.VITE_BASE_API_URL}/streamflow/stations`);
        cache.setData('streamflowStations', streamflowStations)
        return streamflowStations
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
    return await requestWithErrorCatch(`${env.VITE_BASE_API_URL}/streamflow/stations/${id}/report`, 'report');
}

export const getStreamflowReportDataByYear = async (id, year, chart) => {
    try{
        // seven-day-flow or stage
        const streamflowReportResponseForYear = await fetch(`${env.VITE_BASE_API_URL}/streamflow/stations/${id}/report/${chart}/${year}`);
        if(streamflowReportResponseForYear.status !== 200){
            // better errors can be thrown here, if needed/desired, but probably not necessary.
            throw 'Error';
        }
        return streamflowReportResponseForYear.json();
    } catch (e) {
        Notify.create({ message: 'There was a problem fetching streamflow report contents.' });
        return null;
    }
}

export const downloadStreamflowCSV = async (id) => {
    try{
        const response = await fetch(`${env.VITE_BASE_API_URL}/streamflow/stations/${id}/csv`);
        if(!response.ok){
            throw('Error creating CSV File')
        }
        const blob = await response.blob();
        // Set up better error handling! - should notify (could not download csv for station (X))
        const url = window.URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = `streamflow_station_${id}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    } catch (e) {
        Notify.create({ message: 'There was a problem downloading the CSV file.'})
        return null
    }
}

export const getClimateReportDataByYear = async (id, year, chart) => {
    try{
        // snow-survey, snow-water-equivalent, snow-depth, precipitation, temperature
        const streamflowReportResponseForYear = await fetch(`${env.VITE_BASE_API_URL}/climate/stations/${id}/report/${chart}/${year}`);
        if(streamflowReportResponseForYear.status !== 200){
            // better errors can be thrown here, if needed/desired, but probably not necessary.
            throw 'Error';
        }
        return streamflowReportResponseForYear.json();
    } catch (e) {
        Notify.create({ message: 'There was a problem fetching streamflow report contents.' });
        return null;
    }
}

export const downloadClimateCSV = async (id) => {
    try{
        const response = await fetch(`${env.VITE_BASE_API_URL}/climate/stations/${id}/csv`);
        if(!response.ok){
            throw('Error creating CSV File')
        }
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = `climate_station_${id}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    } catch (e) {
        Notify.create({ message: 'There was a problem downloading the CSV file.'})
        return null
    }
}

export const getGroundwaterLevelReportDataByYear = async (id, year, chart) => {
    try{
        const groundwaterReportResponseForYear = await fetch(`${env.VITE_BASE_API_URL}/groundwater/level/stations/${id}/report/${chart}/${year}`);
        if(groundwaterReportResponseForYear.status !== 200){
            // better errors can be thrown here, if needed/desired, but probably not necessary.
            throw 'Error';
        }
        return groundwaterReportResponseForYear.json();
    } catch (e) {
        Notify.create({ message: 'There was a problem fetching streamflow report contents.' });
        return null;
    }
}

export const downloadGroundwaterLevelCSV = async (id) => {
    try{
        const response = await fetch(`${env.VITE_BASE_API_URL}/groundwater/level/stations/${id}/csv`);
        if(!response.ok){
            throw('Error creating CSV File')
        }
        const blob = await response.blob();
        // Set up better error handling! - should notify (could not download csv for station (X))
        const url = window.URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = `groundwater_level_station_${id}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    } catch (e) {
        Notify.create({ message: 'There was a problem downloading the CSV file.'})
        return null
    }
}

export const getSurfaceWaterStations = async () => {
    const cachedSurfaceWaterStations = cache.getData('surfaceWaterStations')
    if (cachedSurfaceWaterStations) {
        return cachedSurfaceWaterStations
    } else {
        const surfaceWaterStations = await requestWithErrorCatch(`${env.VITE_BASE_API_URL}/surface-water/stations`);
        cache.setData('surfaceWaterStations', surfaceWaterStations)
        return surfaceWaterStations
    }
}

export const getSurfaceWaterStationStatistics = async (id) => {
    return await requestWithErrorCatch(`${env.VITE_BASE_API_URL}/surface-water/stations/${id}/station-statistics`);
}

export const getGroundWaterQualityStations = async () => {
    const cachedGroundWaterQualityStations = cache.getData('groundWaterQualityStations')
    if (cachedGroundWaterQualityStations) {
        return cachedGroundWaterQualityStations
    } else {
        const groundWaterQualityStations = await requestWithErrorCatch(`${env.VITE_BASE_API_URL}/groundwater/quality/stations`);
        cache.setData('groundWaterQualityStations', groundWaterQualityStations)
        return groundWaterQualityStations
    }
}

export const getGroundWaterStationStatistics = async (id) => {
    return await requestWithErrorCatch(`${env.VITE_BASE_API_URL}/groundwater/quality/stations/${id}/station-statistics`);
}


/**
 * performs the API call needed to retrieve the groundwater quality
 * report contents for the given point via station ID.
 *
 * @param {string} id - the station ID to be used to fetch report data
 * @returns {object} - categorized groundwater quality report data
 */
export const getGroundWaterQualityReportById = async (id) => {
    return await requestWithErrorCatch(`${env.VITE_BASE_API_URL}/groundwater/quality/stations/${id}/report`, 'report');
}

export const downloadGroundwaterQualityCSV = async (id) => {
    try{
        const response = await fetch(`${env.VITE_BASE_API_URL}/groundwater/quality/stations/${id}/csv`);
        if(!response.ok){
            throw('Error creating CSV File')
        }
        const blob = await response.blob();
        // Set up better error handling! - should notify (could not download csv for station (X))
        const url = window.URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = `groundwater_quality_station_${id}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    } catch (e) {
        Notify.create({ message: 'There was a problem downloading the CSV file.'})
        return null
    }
}

export const getClimateStations = async () => {
    const cachedClimateStations = cache.getData('climateStations')
    if (cachedClimateStations) {
        return cachedClimateStations
    } else {
        const climateStations = await requestWithErrorCatch(`${env.VITE_BASE_API_URL}/climate/stations`);
        cache.setData('climateStations', climateStations)
        return climateStations
    }
}

export const getGroundWaterLevelStations = async () => {
    const cachedGroundWaterLevelStations = cache.getData('groundWaterLevelStations')
    if (cachedGroundWaterLevelStations) {
        return cachedGroundWaterLevelStations
    } else {
        const groundWaterLevelStations = await requestWithErrorCatch(`${env.VITE_BASE_API_URL}/groundwater/level/stations`);
        cache.setData('groundWaterLevelStations', groundWaterLevelStations)
        return groundWaterLevelStations
    }
}

export const getGroundWaterLevelReportById = async (id) => {
    return await requestWithErrorCatch(`${env.VITE_BASE_API_URL}/groundwater/level/stations/${id}/report`, 'report');
}

export const getGroundWaterLevelYearlyData = async (id, year) => {
    return await requestWithErrorCatch(`${env.VITE_BASE_API_URL}/groundwater/level/stations/${id}/report/yearly/${year}`, 'report');
}

export const getSurfaceWaterReportDataById = async (id) => {
    return await requestWithErrorCatch(`${env.VITE_BASE_API_URL}/surface-water/stations/${id}/report`, 'report');
}

export const downloadSurfaceWaterCSV = async (id) => {
    try{
        const response = await fetch(`${env.VITE_BASE_API_URL}/surface-water/stations/${id}/csv`);
        if(!response.ok){
            throw('Error creating CSV File')
        }
        const blob = await response.blob();
        // Set up better error handling! - should notify (could not download csv for station (X))
        const url = window.URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = `surface_water_station_${id}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    } catch (e) {
        Notify.create({ message: 'There was a problem downloading the CSV file.'})
        return null
    }
}

export const getClimateReportById = async (id) => {
    return await requestWithErrorCatch(`${env.VITE_BASE_API_URL}/climate/stations/${id}/report`, 'report');
}
