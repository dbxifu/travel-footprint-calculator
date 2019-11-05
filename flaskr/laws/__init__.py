
# @abc
class BaseEmissionModel():
    def __init__(self, config):  # Constructor
        self.name = config.name
        self.slug = config.slug
        self.color = config.color
        self.selected = config.selected
        self.config = config.config

    def __repr__(self):  # Cast to String
        return "Emission model\n" + \
               "==============\n" + \
               "%s (%s)" % (self.name, self.slug) + \
               repr(self.config)

    # def compute_travel_footprint()
