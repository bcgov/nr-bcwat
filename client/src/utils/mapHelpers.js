export const buildFilteringExpressions = (newFilters) => {
    const mainFilterExpression = buildMainExpression(newFilters)
    const otherFilterExpressions = buildOtherExpressions(newFilters);

    const allExpressions = ["all", mainFilterExpression, otherFilterExpressions];

    // streamflow-specific checks on area
    if('area' in newFilters){
        const areaFilterExpressions = buildAreaExpression(newFilters); 
        if(areaFilterExpressions.length > 0) {
            allExpressions.push(areaFilterExpressions)
        }
    }
    if('year' in newFilters){
        const yearRangeExpression = buildYearExpressions(newFilters);
        if(yearRangeExpression.length){
            allExpressions.push(yearRangeExpression);
        } 
    }
    if('analysesObj' in newFilters){
        const analysisFilter = buildAnalysesObjExpression(newFilters);
        if(analysisFilter.length){
            allExpressions.push(analysisFilter);
        }
    }
    if('quantity' in newFilters){
        const quantityFilter = buildQuantityExpression(newFilters);
        if(quantityFilter.length){
            allExpressions.push(quantityFilter);
        }
    }

    return allExpressions;
}

/**
 * 
 * @param { Object } newFilters - the filter object given to the various pages from the MapFilter.vue component
 * @returns a mapbox array expression built to filter on area ranges provided by the user in the MapFilter.vue component
 */
const buildAreaExpression = (newFilters) => {
    const areaExpression = [];
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
    };
    return ['any', ...areaExpression];
}

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
    return ['any', ...mainFilterExpressions];
}

const buildQuantityExpression = (newFilters) => {
    const quantityExpression = [];
    for(const el in newFilters.quantity){
        const expression = [];
        if(newFilters.quantity[el].value){
            if(newFilters.quantity[el].label.includes('or less')){
                expression.push(["<=", ['get', 'qty'], 10000]);
            }
            else if(newFilters.quantity[el].label.includes('or more')){
                expression.push([">=", ['get', 'qty'], 1000000]);
            } else {
                expression.push(['all', 
                    ['>=', ['get', 'qty'], newFilters.quantity[el].low], 
                    ['<=', ['get', 'qty'], newFilters.quantity[el].high]
                ])
            }
            quantityExpression.push(['any', ...expression]);
        }
    };
    return ['any', ...quantityExpression];
}

const buildYearExpressions = (newFilters) => {
    const yearRange = [];
    if(newFilters.year && newFilters.year[0] && newFilters.year[1]){
        yearRange.push(
            ['>=', ['at', 0, ['get', 'yr']], parseInt(newFilters.year[0].matches)], 
            // ['<=', ['at', 1, ['get', 'yr']], parseInt(newFilters.year[1].matches)]
            ['<=', ['at', ['-', ['length', ['get', 'yr']], 1], ['get', 'yr']], parseInt(newFilters.year[1].matches)]
        );
    }
    return ['all', ...yearRange];
}

const buildAnalysesObjExpression = (newFilters) => {
    const analysisExpressions = [];
    if('analysesObj' in newFilters){
        const expression = [];
        for(const el in newFilters.analysesObj){
            if(newFilters.analysesObj[el].value){
                expression.push(['has', `${newFilters.analysesObj[el].id}`, ['get', 'analysesObj']]);
            }
        }
        if(expression.length) analysisExpressions.push(['any', ...expression])
    }

    return ['any', ...analysisExpressions];
    
}

const buildOtherExpressions = (newFilters) => {
    const filterExpressions = [];
    for(const el in newFilters.other){
        const expression = [];
        newFilters.other[el].forEach(type => {
            if(type.value){
                expression.push(["==", ['get', type.key], type.matches]);
            }
        });
        filterExpressions.push(['any', ...expression])
    };
    return ['all', ...filterExpressions];
}
