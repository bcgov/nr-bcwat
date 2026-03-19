export const addCommas = (str) => {
    const text = str.toString();
    let parts = [text];
    if(text.includes('.')){
        parts = text.split('.');
    }
    const convertedString = parts[0].toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    if(text.includes('.')){
        return `${convertedString}.${parts[1]}`;
    } else {
        return convertedString;
    }
};

export const handleDecimalPlaces = (numToFormat, numDecimals) => {
    if (numToFormat === 0) {
        return numToFormat.toFixed(0);
    }
    else if (numToFormat > 0 && numToFormat < 10**(-1 * numDecimals)) {
        return `< ${10**(-1 * numDecimals)}`
    }
    else {
        return addCommas(numToFormat.toFixed(numDecimals))
    }
};

export const yearRangeString = (yearRange) => {
    if (yearRange.length < 1) {
        return '-'
    } else if (yearRange.length === 1) {
        return `${yearRange[0]}`;
    } else {
        return `${yearRange[0]}-${yearRange[yearRange.length - 1]}`;
    }
};
