export const monthAbbrList = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
];

export const formatDate = (date, format, separator) => {
    const dateParts = format.split(' ');
    const dateString = dateParts.map(part => {
        if(part === 'mm'){
            const monthNum = date.getUTCMonth() + 1;
            return monthNum < 10 ? `0${monthNum}` : monthNum;
        }
        if(part === 'mmm'){
            const monthIdx = date.getUTCMonth();
            return monthAbbrList[monthIdx];
        }
        if(part === 'dd'){
            const day = date.getUTCDate();
            return day < 10 ? `0${day}` : day;
        }
        if(part === 'yyyy'){
            return date.getUTCFullYear();
        }
    }).join(separator)
    return dateString;
}
