import numpy as np
from geopy.distance import great_circle


class EmissionModel():
    def __init__(self, config):
        self.config = config

    def __repr__(self):
        return "Emission model\n" + \
               "==============\n" + \
               repr(self.config)

    def compute_travel_footprint(
            self,
            origin_latitude, origin_longitude,
            destination_latitude, destination_longitude):
        footprint = 0

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

        footprint += self.compute_airplane_footprint(
            origin_airport.latitude,
            origin_airport.longitude,
            destination_airport.latitude,
            destination_airport.longitude
        )

        return footprint

    def compute_airplane_footprint(
            self,
            origin_latitude, origin_longitude,
            destination_latitude, destination_longitude):
        footprint = 0

        distance = self.get_distance_between(
            origin_latitude, origin_longitude,
            destination_latitude, destination_longitude
        )
        footprint += distance  # FIXME

        return footprint

    def get_distance_between(
            self,
            origin_latitude, origin_longitude,
            destination_latitude, destination_longitude):
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
