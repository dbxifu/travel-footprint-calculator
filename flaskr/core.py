import abc
import importlib
from datetime import datetime
from uuid import uuid4

from .content import content


def generate_unique_id():
    """
    :return: a unique identifier that can be sorted chronologically.
    """
    return datetime.now().strftime('%Y-%m-%d_%H:%M:%S_') + str(uuid4())[0:4]


def get_emission_models():
    emission_models_confs = content.models
    emission_models = []

    for model_conf in emission_models_confs:
        model_file = model_conf.file
        the_module = importlib.import_module("flaskr.laws.%s" % model_file)

        model = the_module.EmissionModel(model_conf)
        # model.configure(extra_model_conf)

        emission_models.append(model)

    return emission_models


models = get_emission_models()


# unused
class FootprintEstimatorDriver(abc.ABCMeta):
    @abc.abstractmethod
    def get_travel_footprint(self, from_location, to_location):  # TBD
        pass
