from db_scaling_laws import *
import numpy as np
from geopy.distance import great_circle


# Sample function used by Didier in the prototype.
# We do not use this in the project right now.


def db_get_co2eq_per_city_pairs(in_methods, lat_city1, long_city1, lat_city2,
                                long_city2, rfiatmosfair, dist_min,
                                coeff_connecting_flight, all_economy,
                                seat_category_non_economy,
                                gcd_min_for_business,
                                frac_flights_in_non_economy):
    gcd = great_circle((np.float(lat_city1), np.float(long_city1)),
                       (np.float(lat_city2), np.float(long_city2))).km
    round_trip_distance = gcd * coeff_connecting_flight * 2.
    verbose = True
    co2eq = []

    co2eq_train = 0.
    by_train = False
    if gcd * coeff_connecting_flight < dist_min:
        co2eq_train = 2. * db_get_train_footprint(type_train="mixed",
                                                  distance=gcd * coeff_connecting_flight)
        seat_factor = 0
        seat_cat = "Train seat"
        rfi = 0.
        eq_seat_factor = 0.
        by_train = True
        if verbose:
            print "Minimum distance=", dist_min
            print "Coeff_connecting flight=", coeff_connecting_flight
            print "Selected rfi", rfi
            print "GCD=", gcd
            print "Corrected GCD=", coeff_connecting_flight * gcd
            print "Round trip corrected distance=", 2. * coeff_connecting_flight * gcd
            print "CO2 by train", co2eq_train
            co2eq = np.zeros(len(in_methods))
        return rfi, round_trip_distance, co2eq, co2eq_train, by_train, seat_factor, eq_seat_factor, seat_cat

    seat_factor = 1.
    seat_cat = "economy"
    eq_seat_factor = 1.

    if all_economy: frac_flights_in_non_economy = 0.
    if gcd * coeff_connecting_flight > gcd_min_for_business and not all_economy and not by_train:
        seat_cat = seat_category_non_economy
        seat_factor = db_def_seat_class_coeff_from_defra(
            seat_category_non_economy)

    rfi = 1.9
    if rfiatmosfair: rfi = get_rfi_from_atmosfair(gcd)
    for m in in_methods:
        if verbose:
            print "-------------------------------------------------------------------------------------------"
            print "Method=", m
            print "Minimum distance=", dist_min
            print "Coeff_connecting flight=", coeff_connecting_flight
            print "Selected rfi", rfi
            print "GCD=", gcd
            print "Corrected GCD=", coeff_connecting_flight * gcd
            print "Round trip corrected distance=", 2. * coeff_connecting_flight * gcd
            print "CO2eq per leg without RFI=", db_direct_emission(m, dist_min,
                                                                   coeff_connecting_flight * gcd)
            print "CO2eq=", rfi * 2. * db_direct_emission(m, dist_min,
                                                          coeff_connecting_flight * gcd)
            print "CO2 by train", co2eq_train
            print "Fraction of flights in non economy seating (%)=", frac_flights_in_non_economy
            print "Business correction factor=", seat_factor
            eq_seat_factor = (
                    frac_flights_in_non_economy / 100. * seat_factor + (
                    1. - frac_flights_in_non_economy / 100.))
            print "Equivalent seat factor=", eq_seat_factor
            print "Seat catagory=", seat_cat
            print "CO2eq after correcting for non economy seating=", eq_seat_factor * rfi * 2. * db_direct_emission(
                m, dist_min, coeff_connecting_flight * gcd)
        co2eq.append(
            eq_seat_factor * rfi * 2. * db_direct_emission(m, dist_min,
                                                           coeff_connecting_flight * gcd))

    return rfi, round_trip_distance, co2eq, co2eq_train, by_train, seat_factor, eq_seat_factor, seat_cat
