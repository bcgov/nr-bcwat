import { debounce } from "quasar";
import mapboxgl from 'mapbox-gl';
import bbox from '@turf/bbox';

export const geolocate = async (map) => {
     navigator.geolocation.getCurrentPosition((pos) => {
        const coords = [pos.coords.longitude, pos.coords.latitude];
        map.flyTo({
            center: coords,
            zoom: 10
        });
    });
};

/**
* save map view to sessionStorage to persist between sessions
* debounced 750ms
* @param MapboxGLMap map  mapbox-gl map object
    */
// eslint-disable-next-line prefer-arrow-callback
export const saveMapBounds = debounce(async (map) => {
    // save LngLatBounds array as a JSON string
    let mapBounds = map.getBounds().toArray();
    mapBounds = JSON.stringify(mapBounds);
    window.sessionStorage.setItem('mapBounds', mapBounds);
}, 750);

/**
 * return saved map view from sessionStorage, or null if none exists
 * @return {Array|null} saved map bounds, or null
 */
export const loadMapBounds = () => {
    const mapBounds = window.sessionStorage.getItem('mapBounds');
    if (mapBounds === null) return null;

    return JSON.parse(mapBounds);
};

export const getFilteredPoints = (pointArray, matchFilters, uniqueFilters) => {
    const filteredArray = pointArray.filter(point => {
        // assume point is valid
        let ok = true;
        matchFilters.forEach(filter => {
            if(point.properties[filter.property] === filter.matchValue){
                // mark point as invalid
                ok = false;
                return ok;
            }
        });

        uniqueFilters.forEach(filter => {
            if(filter.property === 'area'){
                if(point.properties[filter.property] <= filter.high && point.properties[filter.property] >= filter.low){
                    return true;
                } else {
                    // mark point as invalid
                    return false;
                }
            }
            if(filter.property === 'qty'){
                if(point.properties[filter.property] <= filter.high && point.properties[filter.property] >= filter.low){
                    ok = false;
                    return ok;
                }
            }
        });

        return ok;
    });

    return filteredArray;
}

/**
 *
 * @param mapObj Mapbox Map
 * @param coords Array of lng, lat coordinates to place the marker
 */
export const createMarker = (marker = null, mapObj, coords) => {
    if(marker){
        marker.remove();
    };
    marker = new mapboxgl.Marker()
        .setLngLat({ lng: coords[0], lat: coords[1]})
        .addTo(mapObj)
    
    return marker
}

/**
 * 
 * @param {Array} filters - 
 * @returns 
 */
export const setPointFilters = (filters) => {
    if(!filters) return [[], []];
    const matchFilterOut = [];
    // matchFilters are a basic set of filters that exclude quantity, area, or year range comparisons. 
    if('matchFilters' in filters){
        // check the point against the filters
        filters?.matchFilters?.forEach(filterCategory => {
            filterCategory.filters.forEach(filter => {
                if(!filter.model){
                    matchFilterOut.push(filter);
                }
            });
        });
    }

    const uniqueFilterOut = [];
    if('uniqueFilters' in filters){
        // WARNING: This section is overly-complex, we should update the 
        // filterableProperties coming from the backend to address some of the object structure here. 

        // area-specific check
        if(filters.uniqueFilters.hasArea){
            if(filters.uniqueFilters.area !== false){
                // lowest vals
                uniqueFilterOut.push({
                    property: 'area',
                    low: filters.uniqueFilters.areaRange.min,
                    high: filters.uniqueFilters.areaRange.max,
                    value: true
                });
            }
        }
        // quantity-specific check
        if(filters.uniqueFilters.hasQuantity){
            if(filters.uniqueFilters.quantity !== false){
                filters.uniqueFilters.quantity.forEach((range, idx) => {
                    if(range.value === false){
                        // lowest vals
                        if(idx === 0){
                            uniqueFilterOut.push({
                                property: 'qty',
                                low: 0,
                                high: 10000,
                                value: range.value
                            });
                        }
                        // highest vals
                        else if(idx === filters.uniqueFilters.quantity.length - 1){
                            uniqueFilterOut.push({
                                property: 'qty',
                                low: 1000000,
                                high: 9999999,
                                value: range.value
                            });
                        }
                        // in between vals
                        else {
                            uniqueFilterOut.push({
                                property: 'qty',
                                low: range.low,
                                high: range.high,
                                value: range.value
                            });
                        }
                    }
                })
            }
        }
        // year range check
        if(filters.uniqueFilters.hasYearRange){}
    }
    return [matchFilterOut, uniqueFilterOut];
}

export const goToLocation = (polygon, mapObj) => {
    const boundingBox = bbox(polygon);
    mapObj.fitBounds(boundingBox, { padding: 50 });
};

export const getFilterablePropertiesByViewType = (viewType, points) => {
    if(!points) return {};

    const defaultFilters = {
        "matchFilters": {},
        "uniqueFilters": {
            "hasArea": false,
            "hasQuantity": false,
            "hasYearRange": true
        }
    };

    const uniqueType = [];
    const uniqueStatus = [];
    const uniqueNetworks = [];

    // generates arrays populated with all possible unique values of the specified properties.
    points.forEach(point => {
        // get unique types -- not watershed!
        if(!uniqueType.includes(point.properties.ty) && (viewType === 'climate' || viewType === 'streams')){
            uniqueType.push(point.properties.ty)
        }
        // get unique statuses
        if(!uniqueStatus.includes(point.properties.status)){
            uniqueStatus.push(point.properties.status)
        }
        // get unique networks
        if(!uniqueNetworks.includes(point.properties.net)){
            uniqueNetworks.push(point.properties.net)
        }
    });

    // build matchFilters list for the filter object
    const matchFilters = [
        {
            "category": "Status",
            "filters": uniqueStatus.map(el => {
                return { label: el, property: 'status', matchValue: el }
            }),
        },
        {
            "category": "Network",
            "filters": uniqueNetworks.map(el => {
                return { label: el, property: 'net', matchValue: el }
            }),
        }
    ]

    // additional checks for page-specific behaviour
    if(viewType === 'climate' || viewType === 'streams'){
        matchFilters.push({
            "category": "Type",
            "filters": uniqueType.map(el => {
                return { label: el, property: 'ty', matchValue: el }
            })
        });
    }

    if(viewType === 'streams') {
        defaultFilters.uniqueFilters.hasArea = true;
    }

    defaultFilters.matchFilters = matchFilters;
    return defaultFilters;
}
