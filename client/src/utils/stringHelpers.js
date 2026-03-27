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
}

export const numberToScientificNotation = (num) => {
    // <span
    //     v-if="+props.monthlyHydrology.waterLicenceMonthlyDisplay[idx] > 9999"
    //     :title="props.monthlyHydrology.waterLicenceMonthlyDisplay[idx]"
    // >
    //     {{ (+props.monthlyHydrology.waterLicenceMonthlyDisplay[idx]).toExponential(2).substring(0, 4) }}x10<sup>{{ (+props.monthlyHydrology.waterLicenceMonthlyDisplay[idx]).toExponential(2).substring(6, (+props.monthlyHydrology.waterLicenceMonthlyDisplay[idx]).toExponential(2).length) }}</sup>
    // </span>
    // <span
    //     v-else
    //     :title="props.monthlyHydrology.waterLicenceMonthlyDisplay[idx]"
    // >
    //     {{ (+props.monthlyHydrology.waterLicenceMonthlyDisplay[idx]) }}
    // </span>
    if(num > 9999){
        const numInScientificNotation = num.toExponential(2);
        const base = numInScientificNotation.substring(0, 4);
        const exponent = numInScientificNotation.substring(6, numInScientificNotation.length);
        return `${base}x10^${exponent}`;
    }
    return num;
}
