import numpy as np
from .travel_emission_linear_fit import EmissionModel as BaseEmissionModel


class EmissionModel(BaseEmissionModel):

    def apply_scaling_law(self, distance, config):
        """
        This interpolation algorithm will handle duplicates
        as one would expect it to do.
        Triplicates and more will only use the outmost values in the list
        and ignore the middle ones.

        And you don't have to provide them in order,
        as this list is also sorted, and thankfully :

        > In Python, when you sort equal values, they will retain their
        > original order in the output.

        :param distance: float
        :param config:
        :return: float
        """

        assert config.points
        assert len(config.points) > 0

        footprint = None

        sample_points = sorted(config.points, key=lambda p: float(p[0]))

        # Numpy!

        previous_point = [0, 0]
        for i, sample_point in enumerate(sample_points):
            if distance <= sample_point[0]:
                t = 0
                if sample_point[0] != previous_point[0]:
                    t = (distance - previous_point[0]) * 1.0 \
                                        / \
                        (sample_point[0] - previous_point[0])

                footprint = previous_point[1] + t * (sample_point[1] - previous_point[1])
                previous_point = sample_point
                break

            previous_point = sample_point

        if footprint is None:
            if len(config.points) == 1:
                last = sample_points[0]
                penu = [0, 0]
            else:
                last = sample_points[-1]
                penu = sample_points[-2]

            t = 0
            if last[0] != penu[0]:
                t = (distance - last[0]) * 1.0 / (last[0] - penu[0])

            footprint = last[1] + t * (last[1] - penu[1])

        return footprint
