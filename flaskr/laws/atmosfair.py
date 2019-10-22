import numpy as np
from geopy.distance import great_circle


class EmissionModel():
    def __init__(self, config):  # Constructor
        self.name = config.name
        self.slug = config.slug
        self.config = config.config

    def __repr__(self):  # Cast to String
        return "Emission model\n" + \
               "==============\n" + \
               "%s (%s)" % (self.name, self.slug) + \
               repr(self.config)

    def compute_travel_footprint(
            self,
            origin_latitude,        # degrees
            origin_longitude,       # degrees
            destination_latitude,   # degrees
            destination_longitude,  # degrees
            prefer_train_under_distance=0,  # meters
    ):
        footprint = 0.0

        #############################################
        # FIXME: find closest airport(s) and pick one
        # We're going to need caching here as well.
        from collections import namedtuple
        origin_airport = namedtuple('Position', [
            'latitude',
            'longitude',
            'address',  # perhaps
        ])
        origin_airport.latitude = origin_latitude
        origin_airport.longitude = origin_longitude
        destination_airport = namedtuple('Position', [
            'latitude',
            'longitude',
            'address',  # perhaps
        ])
        destination_airport.latitude = destination_latitude
        destination_airport.longitude = destination_longitude
        #############################################
        #############################################

        # I.a Train travel footprint
        # ... TODO

        # I.b Airplane travel footprint
        footprint += self.compute_airplane_footprint(
            origin_latitude=origin_airport.latitude,
            origin_longitude=origin_airport.longitude,
            destination_latitude=destination_airport.latitude,
            destination_longitude=destination_airport.longitude,
        )

        # II.a Double the footprint if it's a round-trip
        footprint *= 2.0

        return footprint

    def compute_airplane_footprint(
            self,
            origin_latitude,
            origin_longitude,
            destination_latitude,
            destination_longitude
    ):
        config = self.config.plane_emission_linear_fit

        great_circle_distance = self.get_distance_between(
            origin_latitude, origin_longitude,
            destination_latitude, destination_longitude
        )

        distance = config.connecting_flights_scale * great_circle_distance

        footprint = self.apply_scaling_law(
            distance,
            config.intervals
        )

        return footprint

    def apply_scaling_law(self, distance, intervals):
        footprint = distance
        for interval in intervals:
            if interval.dmin <= distance < interval.dmax:
                offset = interval.offset if interval.offset else 0
                scale = interval.scale if interval.scale else 1
                footprint = footprint * scale + offset
                break

        return footprint

    def get_distance_between(
            self,
            origin_latitude,
            origin_longitude,
            destination_latitude,
            destination_longitude
    ):
        """
        :param origin_latitude:
        :param origin_longitude:
        :param destination_latitude:
        :param destination_longitude:
        :return: Distance in meters between the two locations,
                 along Earth's great circles.
        """
        gcd = great_circle(
            (np.float(origin_latitude), np.float(origin_longitude)),
            (np.float(destination_latitude), np.float(destination_longitude))
        ).m
        return gcd
