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
