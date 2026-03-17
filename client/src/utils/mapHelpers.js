import { debounce } from "quasar";
import { portalHandler } from '@/utils/reactor.js';

export const buildFilteringExpressions = (newFilters, isWaterPortal) => {
    const mainFilterExpression = buildMainExpression(newFilters);
    const otherFilterExpressions = buildOtherExpressions(newFilters);

    const allExpressions = [];

    if(mainFilterExpression.length > 1 && !isWaterPortal){
        allExpressions.push(mainFilterExpression);
    }
    if(otherFilterExpressions.length > 1){
        allExpressions.push(otherFilterExpressions);
    }

    // streamflow-specific checks on area
    if('area' in newFilters && isWaterPortal && portalHandler.viewType === 'streams'){
        const areaFilterExpressions = buildAreaExpression(newFilters, isWaterPortal);
        if(areaFilterExpressions.length > 1) {
            allExpressions.push(areaFilterExpressions)
        }
    }
    if('year' in newFilters){
        const yearRangeExpression = buildYearExpressions(newFilters);
        if(yearRangeExpression.length > 1){
            allExpressions.push(yearRangeExpression);
        }
    }
    // watershed-specific check on quantity
    if('quantity' in newFilters && !isWaterPortal){
        const quantityFilter = buildQuantityExpression(newFilters);
        if(quantityFilter.length > 1){
            allExpressions.push(quantityFilter);
        }
    }

    return ['all', ...allExpressions];
}

/**
 *
 * @param { Object } newFilters - the filter object given to the various pages from the MapFilter.vue component
 * @returns a mapbox array expression built to filter on area ranges provided by the user in the MapFilter.vue component
 */
const buildAreaExpression = (newFilters) => {
    const areaExpression = [];
    let allTrue = true;
    for(const el in newFilters.area){
        const expression = [];
        if(newFilters.area[el].value){
            if(newFilters.area[el].label.includes('or less')){
                expression.push(["<=", ['get', 'area'], newFilters.area[el].high]);
            }
            else if(newFilters.area[el].label.includes('or more')){
                expression.push([">=", ['get', 'area'], newFilters.area[el].low]);
            } else {
                expression.push(['all',
                    ['>=', ['get', 'area'], newFilters.area[el].low],
                    ['<=', ['get', 'area'], newFilters.area[el].high]
                ])
            }
            areaExpression.push(['any', ...expression]);
        }
        else {
            allTrue = false;
        }

    };
    if (!allTrue) {
        return ['any', ...areaExpression];
    }
    else {
        // If all of the filters are true, don't filter at all
        return [];
    }}

const buildMainExpression = (newFilters) => {
    const mainFilterExpressions = [];
    // filter expression builder for the main buttons:
    newFilters.buttons.forEach(el => {
        if(el.value){
            el.matches.forEach(match => {
                mainFilterExpressions.push(["==", ['get', el.key], match]);
            })
        }
    });
    if(mainFilterExpressions.length === 0){
        mainFilterExpressions.push(["==", ['get', 'ty'], 'none'])
    }
    return ['any', ...mainFilterExpressions];
}

const buildQuantityExpression = (newFilters) => {
    const quantityExpression = [];
    let allTrue = true;
    for(const el in newFilters.quantity){
        const expression = [];
        if(newFilters.quantity[el].value){
            if(newFilters.quantity[el].label.includes('or less')){
                expression.push(["<=", ['get', 'qty'], 10000]);
            }
            else if(newFilters.quantity[el].label.includes('or more')){
                expression.push([">=", ['get', 'qty'], 1000000]);
            }
            else {
                expression.push(['all',
                    ['>=', ['get', 'qty'], newFilters.quantity[el].low],
                    ['<=', ['get', 'qty'], newFilters.quantity[el].high]
                ])
            }
            quantityExpression.push(['any', ...expression]);
        }
        else {
            allTrue = false;
        }
    };
    if (!allTrue) {
        // If all of the filters are true, don't filter at all
        return ['any', ...quantityExpression];
    }
    else {
        return [];
    }
}

const buildYearExpressions = (newFilters) => {
    const yearRange = [];
    if(newFilters.year){
        if(newFilters.year[0]){
            yearRange.push(['>=', ['at', 0, ['get', 'yr']], parseInt(newFilters.year[0].matches)])
        }
        if(newFilters.year[1]){
            yearRange.push(['<=', ['at', ['-', ['length', ['get', 'yr']], 1], ['get', 'yr']], parseInt(newFilters.year[1].matches)]);
        }
    }
    return ['all', ...yearRange];
}

const buildOtherExpressions = (newFilters) => {
    const filterExpressions = [];
    for(const el in newFilters.other){
        if(newFilters.other[el].length){
          const expression = [];
          newFilters.other[el].forEach(type => {
              if (type.value) {
                  expression.push(["==", ['get', type.key], type.matches]);
              }
          });
          filterExpressions.push(['any', ...expression])
        }
    };

    return ['all', ...filterExpressions];
}

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
