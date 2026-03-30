import { Notify } from 'quasar';
import { env } from '@/env';
import cache from './cache';

const requestWithErrorCatch = async (url, fetchType) => {
    try {
        const response = await fetch(url);
        if (response.status === 404) {
            if (fetchType === 'report') throw { message: 'No report data for the selected point. Try selecting another point.' };
            else if (fetchType === 'watershedLookup') throw { message: 'No watershed data for selected point, please ensure you are selecting a point within highlighted region'};
            else if (fetchType !== 'search') throw { message: 'No data found.' };
        } else if (response.status === 500) {
            if (fetchType === 'report') throw { message: 'There was a problem getting report data. Please try again later. ' };
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
    return await requestWithErrorCatch(`${env.VITE_BASE_API_URL}/watershed/search?wfi=${wfi}`, 'search')
}

export const getWatershedByWFI = async (wfi) => {
    return await requestWithErrorCatch(`${env.VITE_BASE_API_URL}/watershed/${wfi}`)
}

export const getWatershedLicenceBySearch = async (licence_no) => {
    return await requestWithErrorCatch(`${env.VITE_BASE_API_URL}/watershed/licences/search?licence_no=${licence_no}`, 'search')
}

export const getPlaceByNameSearch = async (location_name) => {
    return await requestWithErrorCatch(`${env.VITE_BASE_API_URL}/watershed/location/search?location_name=${location_name}`, 'search')
}

export const getWatershedByLatLng = async (lngLat) => {
    return await requestWithErrorCatch(`${env.VITE_BASE_API_URL}/watershed/?lat=${lngLat.lat}&lng=${lngLat.lng}`, 'watershedLookup');
}

export const getWatershedReportByWFI = async (wfi) => {
    return await requestWithErrorCatch (`${env.VITE_BASE_API_URL}/watershed/${wfi}/report`, 'report');
}

export const downloadWatershedReportPolygon = async (wfi, format) => {
    return await fetch(`${env.VITE_BASE_API_URL}/watershed/${wfi}/report/download_watershed/${format}`);
}

// PDF generation
/**
 * Get watershed report PDF file
 *
 * @param {mapboxgl.LngLat} lngLat - LngLat object with query coordinates
 * @param {string} wfi - WFI corresponding to a watershed
 * @param {string} watershedName - display name for the watershed
 * @param {string} fwa - FWA code for the watershed
 * @param {object} userCustomization - user options from "Customize your report" feature
 * @returns {Promise} - promise resolving to the watershed report PDF file
 */
export const getWatershedReportPdf = async (
    lngLat,
    wfi,
    watershedName,
    title = "",
    notes = "",
    userCustomization = {}
) => {
    const { lng, lat } = lngLat;

    return await fetch(
        `${env.VITE_BASE_API_URL}/watershed/${wfi}/report/pdf`,
        {
            method: "POST",
            responseType: "arraybuffer",
            headers: {
                Accept: "application/pdf",
                "Content-Type": "application/json",
            },
            // old params:
            // ?lng=${lng}&lat=${lat}&watershedName=${watershedName}&title=${title}&notes=${notes}&userCustomization=${encodeURIComponent(JSON.stringify(userCustomization))}
            body: JSON.stringify({
                lng,
                lat,
                watershedName,
                title,
                notes,
                userCustomization
            }),
        },
    ).then(async (res) => {
        if(res.status > 299){
            return null
        } else {
            // Get the response body as a Blob
            const blob = await res.blob();
            return blob;
        }
    });
};

export const downloadCsvWatershedReport = async (wfi) => {
    try {
        const response = await fetch(`${env.VITE_BASE_API_URL}/watershed/${wfi}/report/csv`);
        if (!response.ok) {
            throw('Error creating CSV File')
        }
        const blob = await response.blob();
        const blobUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = blobUrl;
        a.download = `watershed_report_${wfi}.zip`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(blobUrl);
    } catch (e) {
        Notify.create({ message: 'There was a problem downloading the CSV files for this report. Please try again later.'});
        return null;
    }
}

export const getWaterPortalStations = async (viewType) => {
    let response = [];
    if (viewType === 'streams') response = await getStreamflowStations();
    else if (viewType === 'wells') response = await getGroundWaterLevelStations();
    else if (viewType === 'surface') response = await getSurfaceWaterStations();
    else if (viewType === 'ground') response = await getGroundWaterQualityStations();
    else if (viewType === 'climate') response = await getClimateStations();
    return response;
}

export const getWaterPortalReportDataByIdAndType = async (id, viewType) => {
    let response = [];
    if (viewType === 'streams') response = await getStreamflowReportDataById(id);
    else if (viewType === 'wells') response = await getGroundWaterLevelReportById(id);
    else if (viewType === 'surface') response = await getSurfaceWaterReportDataById(id);
    else if (viewType === 'ground') response = await getGroundWaterQualityReportById(id);
    else if (viewType === 'climate') response = await getClimateReportById(id);
    return response;
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
    try {
        // seven-day-flow or stage
        const streamflowReportResponseForYear = await fetch(`${env.VITE_BASE_API_URL}/streamflow/stations/${id}/report/${chart}/${year}`);
        if (streamflowReportResponseForYear.status !== 200) {
            // better errors can be thrown here, if needed/desired, but probably not necessary.
            throw 'Error';
        }
        return streamflowReportResponseForYear.json();
    } catch (e) {
        Notify.create({ message: 'There was a problem fetching streamflow report contents.' });
        return null;
    }
}

export const getClimateReportDataByYear = async (id, year, chart) => {
    try {
        // snow-survey, snow-water-equivalent, snow-depth, precipitation, temperature
        const streamflowReportResponseForYear = await fetch(`${env.VITE_BASE_API_URL}/climate/stations/${id}/report/${chart}/${year}`);
        if (streamflowReportResponseForYear.status !== 200) {
            // better errors can be thrown here, if needed/desired, but probably not necessary.
            throw 'Error';
        }
        return streamflowReportResponseForYear.json();
    } catch (e) {
        Notify.create({ message: 'There was a problem fetching streamflow report contents.' });
        return null;
    }
}

export const getGroundwaterLevelReportDataByYear = async (id, year, chart) => {
    try {
        const groundwaterReportResponseForYear = await fetch(`${env.VITE_BASE_API_URL}/groundwater/level/stations/${id}/report/${chart}/${year}`);
        if (groundwaterReportResponseForYear.status !== 200) {
            // better errors can be thrown here, if needed/desired, but probably not necessary.
            throw 'Error';
        }
        return groundwaterReportResponseForYear.json();
    } catch (e) {
        Notify.create({ message: 'There was a problem fetching streamflow report contents.' });
        return null;
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

export const getClimateReportById = async (id) => {
    return await requestWithErrorCatch(`${env.VITE_BASE_API_URL}/climate/stations/${id}/report`, 'report');
}

export const downloadCSVByTypeAndId = async (type, id) => {
    let url = '';
    let filename = '';

    if (type === 'climate') {
        url = `${env.VITE_BASE_API_URL}/climate/stations/${id}/csv`;
        filename = `climate_station_${id}`;
    } else if (type === 'surface') {
        url = `${env.VITE_BASE_API_URL}/surface-water/stations/${id}/csv`;
        filename = `surface_water_station_${id}`;
    } else if (type === 'wells') {
        url = `${env.VITE_BASE_API_URL}/groundwater/level/stations/${id}/csv`;
        filename = `groundwater_level_station_${id}`;
    } else if (type === 'ground') {
        url = `${env.VITE_BASE_API_URL}/groundwater/quality/stations/${id}/csv`;
        filename = `groundwater_quality_station_${id}`;
    } else if (type === 'streams') {
        url = `${env.VITE_BASE_API_URL}/streamflow/stations/${id}/csv`;
        filename = `streamflow_station_${id}`;
    } else {
        return;
    }

    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw('Error creating CSV File')
        }
        const blob = await response.blob();
        const blobUrl = window.URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = blobUrl;
        a.download = `${filename}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(blobUrl);
    } catch (e) {
        Notify.create({ message: 'There was a problem downloading the CSV file.'})
        return null
    }
}
