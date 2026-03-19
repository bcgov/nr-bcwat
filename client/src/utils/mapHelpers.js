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
        // assume point is valid to start
        let ok = true;

        matchFilters.forEach(category => {
            category.filters.forEach(filter => {
                // when the model is FALSE (off)...
                if (!filter.model) {
                    // then when the point HAS that filter property value, mark as invalid
                    if (point.properties[filter.property] === filter.matchValue) {
                        // mark point as invalid
                        ok = false
                    }
                }
            });
        });

        if (uniqueFilters.hasQuantity) {
            uniqueFilters.quantity.forEach(quantity => {
                // if the quanity filter is off...
                if (!quantity.value) {
                    // then if the point quantity is WITHIN the range, mark as invalid
                    if (point.properties.qty <= quantity.high && point.properties.qty >= quantity.low) {
                        ok = false;
                    }
                }
            });
        }
        if (uniqueFilters.hasArea) {
            uniqueFilters.areaRange.forEach(area => {
                // if the area filter is off...
                if (!area.value) {
                    // then if the point area is above the filter high or below the filter low, mark as invalid
                    if (point.properties.area <= area.high && point.properties.area >= area.low) {
                        ok = false;
                    }
                }
            });
        }
        if (uniqueFilters.hasYearRange) {
            const yearMin = uniqueFilters.yearRange.min;
            const yearMax = uniqueFilters.yearRange.max;
            let anyYearInRange = false;
            point.properties.yr.forEach(year => {
                if (year >= yearMin && year <= yearMax) {
                    anyYearInRange = true;
                }
            });
            if (!anyYearInRange) {
                ok = false;
            }
        }
        //     if (filterKey === 'yearRange') {
        //         if (point.properties.yr.length > 0) {
        //             const pointYearMin = parseInt(point.properties.yr[0]);
        //             const pointYearMax = parseInt(point.properties.yr[point.properties.yr.length - 1]);

        //             if (pointYearMin <= uniqueFilters[filterKey].high && pointYearMin >= uniqueFilters[filterKey].low && pointYearMax >= uniqueFilters[filterKey].low && pointYearMax <= uniqueFilters[filterKey].high) {
        //                 return false;
        //             }
        //         }
        //     }
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
    if (marker) {
        marker.remove();
    };
    marker = new mapboxgl.Marker()
        .setLngLat({ lng: coords[0], lat: coords[1]})
        .addTo(mapObj)

    return marker
};

export const goToLocation = (polygon, mapObj) => {
    const boundingBox = bbox(polygon);
    mapObj.fitBounds(boundingBox, { padding: 50 });
};

/**
 *
 * @param viewType the current water portal view type
 * @param points list of points to generate filters from
 * @returns {Object} filterable properties object
 */
export const getFilterablePropertiesByViewType = (viewType, points) => {
    if (!points) return {};

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
        if (!uniqueType.includes(point.properties.ty) && (viewType === 'climate' || viewType === 'streams')) {
            uniqueType.push(point.properties.ty)
        }
        // get unique statuses
        if (!uniqueStatus.includes(point.properties.status)) {
            uniqueStatus.push(point.properties.status)
        }
        // get unique networks
        if (!uniqueNetworks.includes(point.properties.net)) {
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
    if (viewType === 'climate' || viewType === 'streams') {
        matchFilters.push({
            "category": "Type",
            "filters": uniqueType.map(el => {
                return { label: el, property: 'ty', matchValue: el }
            })
        });
    }

    // add the year range
    const min = points.filter(point => {
        return point.properties.yr.length > 0;
    }).map(point => point.properties.yr[0]);

    const max = points.filter(point => {
        return point.properties.yr.length > 0;
    }).map(point => point.properties.yr[point.properties.yr.length - 1]);

    defaultFilters.uniqueFilters.yearRange = {
        min: Math.min(...min),
        max: Math.max(...max)
    }

    if (viewType === 'streams') {
        defaultFilters.uniqueFilters.hasArea = true;
    }

    defaultFilters.matchFilters = matchFilters;
    return defaultFilters;
}
