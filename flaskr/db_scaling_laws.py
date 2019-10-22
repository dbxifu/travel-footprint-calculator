import numpy as np


# Legacy code, for inspiration.  Not actually used.


def correct_gcd_from_icao(d):
    if d <= 550.:
        return d + 50.
    elif 550. < d < 5500.:
        return d + 100.
    elif d >= 5500.:
        return d + 125.


def db_def_seat_class_coeff_from_defra(category="economy"):
    seat_coeff_defra = [0.073195, 0.11711, 0.21226, 0.29276]
    seat_category = ["economy", "premium ", "business ", "first"]
    assert category in seat_category

    if category.lower() == "economy":
        return 1.
    elif category.lower() == "premium":
        return seat_coeff_defra[1] / seat_coeff_defra[0]
    elif category.lower() == "business":
        return seat_coeff_defra[2] / seat_coeff_defra[0]
    elif category.lower() == "first":
        return seat_coeff_defra[3] / seat_coeff_defra[0]


def db_direct_emission(method, dist_min, x):
    if x < dist_min:
        return 0.

    # x is the GCD I calculate
    if method == "ICAO":
        if x < 1000.:
            return 23.339 + 0.10108 * x
        elif 1000. <= x < 4000.:
            return 70.851 + 0.050821 * x
        elif x > 4000.:
            return 121.08 + 0.035461 * x

    if method == "DEFRA":
        if x < 500.:
            return x * 0.13483
        elif 500. <= x < 3700.:
            return x * 0.08233
        elif x >= 3700.:
            return x * 0.5 * (0.0792 + 0.073195)

    if method == "ATMOSFAIR":
        x += 50.
        if x < 1000.:
            return 25.922 + 0.079107 * x
        elif 1000. <= x < 4000.:
            return 35.041 + 0.066183 * x
        elif x > 4000.:
            return (-80.835) + 0.095998 * x

    if method == "ADEME":

        d_corr = correct_gcd_from_icao(x)

        # This is from table 21

        if x < 1000.:
            coeff_emission = [117., 187, 141, 223.]
            return np.mean(np.multiply(coeff_emission, d_corr / 1000.))
        elif 1000. <= x < 2000.:
            coeff_emission = [95, 254, 123, 117, 161]
            return np.mean(np.multiply(coeff_emission, d_corr / 1000.))
        elif 2000. <= x < 3000.:
            coeff_emission = [91, 101, 109]
            return np.mean(np.multiply(coeff_emission, d_corr / 1000.))
        elif 3000. <= x < 4000.:
            coeff_emission = [99, 99, 105]
            return np.mean(np.multiply(coeff_emission, d_corr / 1000.))
        elif 4000. <= x < 5000.:
            coeff_emission = [90, 126, 153]
            return np.mean(np.multiply(coeff_emission, d_corr / 1000.))
        elif 5000. <= x < 6000.:
            coeff_emission = [88, 98, 150]
            return np.mean(np.multiply(coeff_emission, d_corr / 1000.))
        elif 6000. <= x < 7000.:
            coeff_emission = [82, 100]
            return np.mean(np.multiply(coeff_emission, d_corr / 1000.))
        elif 7000. <= x < 8000.:
            coeff_emission = [87, 91]
            return np.mean(np.multiply(coeff_emission, d_corr / 1000.))
        elif 8000. <= x < 9000.:
            coeff_emission = [87, 95]
            return np.mean(np.multiply(coeff_emission, d_corr / 1000.))
        elif 9000. <= x < 10000.:
            coeff_emission = [73, 83]
            return np.mean(np.multiply(coeff_emission, d_corr / 1000.))
        elif 10000. <= x < 11000.:
            coeff_emission = [95]
            return np.mean(np.multiply(coeff_emission, d_corr / 1000.))
        elif x >= 11000.:
            coeff_emission = [94]
            return np.mean(np.multiply(coeff_emission, d_corr / 1000.))
