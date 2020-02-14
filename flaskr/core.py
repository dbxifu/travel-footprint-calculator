import abc
import importlib
from os.path import isfile, join, abspath, dirname
from datetime import datetime
from uuid import uuid4

from .content import get_path, content


hit_count_path = get_path("VISITS")


def generate_unique_id():
    """
    :return: a unique identifier that can be sorted chronologically.
    """
    return u"%s" % (
            datetime.now().strftime('%Y-%m-%d_%H:%M:%S_') + str(uuid4())[0:4]
    )


def get_emission_models():
    emission_models_confs = content.models
    emission_models = []

    for model_conf in emission_models_confs:
        model_file = model_conf.file
        the_module = importlib.import_module("flaskr.laws.%s" % model_file)

        model = the_module.EmissionModel(model_conf, content.shared_config)
        # model.configure(extra_model_conf)

        emission_models.append(model)

    return emission_models


models = get_emission_models()


def get_hit_counter():
    hit_count = 1
    if isfile(hit_count_path):
        with open(hit_count_path) as hcf:
            hit_count = int(hcf.read().strip())

    return hit_count


def increment_hit_counter():
    if isfile(hit_count_path):
        hit_count = get_hit_counter()
        hit_count += 1
    else:
        hit_count = 1

    with open(hit_count_path, 'w') as hcf:
        hcf.write(str(hit_count))

    return hit_count


# # unused
# class FootprintEstimatorDriver(abc.ABCMeta):
#     @abc.abstractmethod
#     def get_travel_footprint(self, from_location, to_location):  # TBD
#         pass
