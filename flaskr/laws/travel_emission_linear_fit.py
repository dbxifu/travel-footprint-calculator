import numpy as np
from geopy.distance import great_circle

from flaskr.laws import BaseEmissionModel


class EmissionModel(BaseEmissionModel):
    # @abc
    def compute_travel_footprint(
            self,
            origin_latitude,        # degrees
            origin_longitude,       # degrees
            destination_latitude,   # degrees
            destination_longitude,  # degrees
            extra_config=None,
    ):
        footprint = 0.0
        distance = 0.0

        #############################################
        # TODO (?): find closest airport(s) and pick one
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

        # Let's start by computing the distance between the locations
        great_circle_distance = self.get_distance_between(
            origin_latitude=origin_airport.latitude,
            origin_longitude=origin_airport.longitude,
            destination_latitude=destination_airport.latitude,
            destination_longitude=destination_airport.longitude,
        )
        distance += great_circle_distance

        use_train = False
        use_plane = False
        if distance < extra_config['use_train_below_distance']:
            use_train = True
        else:
            use_plane = True

        # I.a Train travel footprint
        if use_train:
            footprint += self.compute_train_footprint(
                distance=great_circle_distance
            )
        # I.b Airplane travel footprint
        elif use_plane:
            footprint += self.compute_airplane_footprint(
                distance=great_circle_distance
            )

        # II.a Double it up since it's a round-trip
        footprint *= 2.0
        distance *= 2.0

        return {
            'distance_km': distance,
            'co2eq_kg': footprint,
            'train_trips': 1 if use_train else 0,  # amount of round trips
            'plane_trips': 1 if use_plane else 0,  # amount of round trips
        }

    def compute_train_footprint(self, distance):
        return distance * 0.020

    def compute_airplane_footprint(
            self,
            distance
    ):
        config = self.config.plane_emission_linear_fit

        distance = config.connecting_flights_scale * distance

        footprint = self.compute_airplane_distance_footprint(distance, config)

        return footprint

    def compute_airplane_distance_footprint(self, distance, config=None):
        """
        :param distance: in km
        :param config:
        :return:
        """
        if config is None:
            config = self.config.plane_emission_linear_fit
        distance = distance * config.scale_before + config.offset_before
        footprint = self.apply_scaling_law(distance, config)
        # We can totally ignore RFI in config by commenting the line below
        footprint = self.adjust_footprint_for_rfi(footprint, config)

        return footprint

    def adjust_footprint_for_rfi(self, footprint, config):
        return config.rfi * footprint

    def apply_scaling_law(self, distance, config):
        """
        :param distance: in km
        :param config:
        :return: float
        """
        footprint = distance
        for interval in config.intervals:
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
        :return: Distance in kilometers between the two locations,
                 along Earth's great circles.
        """
        return great_circle(
            (np.float(origin_latitude), np.float(origin_longitude)),
            (np.float(destination_latitude), np.float(destination_longitude))
        ).kilometers
