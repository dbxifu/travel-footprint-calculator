from collections import namedtuple
from os import getenv
from os.path import abspath, dirname, join

from yaml import safe_load as yaml_safe_load

BASE_URL = getenv('BASE_URL')
if BASE_URL is None:
    raise EnvironmentError("BASE_URL is not set")

PROJECT_DIRECTORY = abspath(dirname(dirname(__file__)))


def get_path(relative_path):
    """
    Absolutize a relative path to this project's root directory.
    """
    return abspath(join(PROJECT_DIRECTORY, relative_path))


with open(get_path('content.yml'), 'r') as content_file:
    content_dict = yaml_safe_load(content_file.read())


class Struct(object):
    def __new__(cls, data):
        if isinstance(data, dict):
            return namedtuple(
                'Struct', data.keys()
            )(
                *(Struct(val) for val in data.values())
            )
        elif isinstance(data, (tuple, list, set, frozenset)):
            return type(data)(Struct(_) for _ in data)
        else:
            return data


content = Struct(content_dict)


# For Python3?
# def dict2obj(d):
#     """
#     Convert a dict to an object
#
#     >>> d = {'a': 1, 'b': {'c': 2}, 'd': ["hi", {'foo': "bar"}]}
#     >>> obj = dict2obj(d)
#     >>> obj.b.c
#     2
#     >>> obj.d
#     ["hi", {'foo': "bar"}]
#     """
#     try:
#         d = dict(d)
#     except (TypeError, ValueError):
#         return d
#     obj = Object()
#     for k, v in d.iteritems():
#         obj.__dict__[k] = dict2obj(v)
#     return obj
