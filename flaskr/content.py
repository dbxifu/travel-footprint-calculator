from collections import namedtuple
from yaml import safe_load as yaml_safe_load

from core import get_path

with open(get_path('content.yml'), 'r') as content_file:
    content_dict = yaml_safe_load(content_file.read())


class Struct(object):
    def __new__(cls, data):
        if isinstance(data, dict):
            return namedtuple(
                'Struct', data.iterkeys()
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
