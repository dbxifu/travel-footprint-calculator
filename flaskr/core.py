import abc
from datetime import datetime
from uuid import uuid4


def generate_unique_id():
    """
    :return: a unique identifier that can be sorted chronologically.
    """
    return datetime.now().strftime('%Y-%m-%d_%H:%M:%S_') + str(uuid4())[0:4]


# def estimate_travel_carbon_footprint(from_address, to_address):
#     return 1


class FootprintEstimatorDriver(abc.ABCMeta):
    @abc.abstractmethod
    def get_travel_footprint(self, from_location, to_location):  # TBD
        pass
