
# @abc
class BaseEmissionModel():
    def __init__(self, config, shared_config):  # Constructor
        self.name = config.name
        self.description = config.description
        self.slug = config.slug
        self.color = config.color
        self.selected = config.selected
        self.config = config.config
        # Here you'll get what's under `model_shared_config:` in content.yml
        self.shared_config = shared_config

    def __repr__(self):  # Cast to String
        return "Emission model\n" + \
               "==============\n" + \
               "%s (%s)" % (self.name, self.slug) + \
               repr(self.config)

    # def compute_travel_footprint()
