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
