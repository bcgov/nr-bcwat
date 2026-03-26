import filenamify from 'filenamify';

/**
 * Format report filename string to a valid filename
 *
 * @param {string} userFileName - user defined file name
 * @param {string} defaultFileName - default file name
 * @returns {string} - formatted valid filename
 */
export const reportFileName = (userFileName, defaultFileName = `report_${Date.now().toLocaleString('en-CA')}`) => {
    const reportFileName = filenamify(userFileName, { replacement: '_' });
    return reportFileName || defaultFileName;
};
