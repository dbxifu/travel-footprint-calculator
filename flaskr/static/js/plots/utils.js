/** POLYFILLS **/
Math.log10 = Math.log10 || function(x) { return Math.log(x) * Math.LOG10E; };

/**
 * Useful for axes' domains on plots.
 * @param value
 * @returns {number}
 */
const ceil_value_to_magnitude = function (value) {
    let sign = 1;
    if (value < 0) {
        value = Math.abs(value);
        sign = -1;
    }
    if (value < 1) {
        return sign;
    }

    const low = Math.pow(10, Math.floor(Math.log10(value)));

    let cursor = low;
    let noloop = 0;
    while ((cursor < value) && (noloop <= 100)) {
        cursor += 0.1 * low;
        noloop += 1;
    }

    return sign * cursor;
};
