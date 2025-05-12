/**
 * scientific notation number formatter
 */
import * as d3 from "d3";

/**
 * return a string in the format  <base>×10<exponent>
 * @param  {Number} d unformatted number
 * @return {String}   scientific notation-formatted string
 */
export const sciNotationConverter = (d) => {
    const superScript = ["⁰", "¹", "²", "³", "⁴", "⁵", "⁶", "⁷", "⁸", "⁹"];
    if (d < 1000) {
        // scientific notation not necessary
        return d;
    }
    const exponentFmt = d3.format(".1e"); // temp function
    const values = exponentFmt(d).toString().split("e+"); // this assumes it's always > 1
    let [base, exponent] = values;
    base = parseInt(base, 10);
    exponent = exponent.split("");
    exponent = exponent.map((n) => superScript[n]).join("");
    return `${base}×10${exponent}`;
};
