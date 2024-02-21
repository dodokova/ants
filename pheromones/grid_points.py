import math
from decimal import *

import numpy as np
import scipy.stats as stats
from typing import List
from helper_functions import get_point_distance
from settings import Settings


class GridPoint:
    def __init__(
        self,
        numerical_step_size,
        x,
        y,
        distance=None,
        influence_rate=None,
        is_relevant=True,
        for_position=None,
    ):
        self.x = int(x)
        self.y = int(y)
        self.distance = distance
        self.distances = []
        self.gaussian_values = []
        self.influence_rate = influence_rate
        self.amount = None
        self.numerical_step_size = numerical_step_size
        self.is_relevant = is_relevant
        self.for_position = for_position

    def __str__(self):
        return "Grid point: [" + str(self.x) + ", " + str(self.y) + "]"

    def add_distance(self, distance):
        self.distances.append(distance)

    def set_is_relevant(self, is_relevant):
        self.is_relevant = is_relevant

    def set_influence_rate(self, influence_rate):
        self.influence_rate = Decimal(influence_rate)

    def get_distance(self, position):
        regular_point = [
            self.x * self.numerical_step_size,
            self.y * self.numerical_step_size,
        ]
        return get_point_distance(position, regular_point)

    def set_and_get_distance(self, position):
        self.distance = self.get_distance(position)
        return self.distance

    def add_distances_for_positions(self, positions):
        for position in positions:
            distance = self.get_distance(position)
            self.add_distance(Decimal(distance))

    def set_gaussian_for_distances(self, sigma, max_distance):
        gaussian_values = stats.norm.pdf(
            np.array(self.distances, dtype=float), loc=0.0, scale=float(sigma)
        )
        self.gaussian_values = np.array(
            [
                (
                    Decimal(gaussian)
                    if self.distances[index] <= max_distance
                    else Decimal(0)
                )
                for index, gaussian in enumerate(gaussian_values)
            ]
        )

    def set_influence_rate_due_to_gaussian(self, totals):
        self.influence_rate = np.sum(
            np.array(self.gaussian_values) / np.array(totals)
        ) / len(self.gaussian_values)

    def set_amount_due_to_influence_rate(self, total_amount: Decimal):
        self.amount = self.influence_rate * total_amount


class GridPoints:
    def __init__(self, numerical_step_size, max_distance=None):
        self.numerical_step_size = numerical_step_size
        self.total_distance = 0
        self.max_distance = max_distance or 2 * (
            self.numerical_step_size**2
        ) ** Decimal(0.5)
        self.grid_points = []
        self.set_grid_points()

    def set_grid_points(self):
        raise NotImplementedError

    def get_grid_value_for_position(self, grid_position_x, grid_position_y):
        return [
            grid_position_x / self.numerical_step_size,
            grid_position_y / self.numerical_step_size,
        ]

    def get_real_value_for_grid_point(self, position_x, position_y):
        return [
            position_x * self.numerical_step_size,
            position_y * self.numerical_step_size,
        ]

    def get_smaller_grid_point_in_one_direction(self, position):
        if position % self.numerical_step_size == 0:
            return position / self.numerical_step_size
        point = math.floor(position)
        # necessary if the step is greater than 1
        while (point % self.numerical_step_size) != 0:
            point = point - 1
        while (position - point) > self.numerical_step_size:
            point = point + self.numerical_step_size
        return point / self.numerical_step_size

    def get_larger_grid_point_in_one_direction(self, position):
        if position % self.numerical_step_size == 0:
            return position / self.numerical_step_size
        point = math.ceil(position)
        # necessary if the step is greater than 1
        while (point % self.numerical_step_size) != 0:
            point = point + 1
        while (point - position) > self.numerical_step_size:
            point = point - self.numerical_step_size
        return point / self.numerical_step_size

    def set_distance_to_points(self, position):
        for grid_point in self.grid_points:
            self.total_distance += grid_point.set_and_get_distance(position)

    def set_influence_rate_to_points(self):
        total_influence = 0
        for grid_point in self.grid_points:
            normalized_distance = grid_point.distance / self.max_distance
            total_influence += 1 - normalized_distance
        for grid_point in self.grid_points:
            influence = 1 - (grid_point.distance / self.max_distance)
            grid_point.set_influence_rate(influence / total_influence)


class GridPointsForPosition(GridPoints):
    def __init__(self, numerical_step_size, position):
        self.position_x = position[0]
        self.position_y = position[1]
        super().__init__(numerical_step_size)

    def set_grid_points(self):
        top_left_point_x = self.get_smaller_grid_point_in_one_direction(self.position_x)
        top_left_point_y = self.get_smaller_grid_point_in_one_direction(self.position_y)
        self.grid_points = [
            GridPoint(
                self.numerical_step_size,
                top_left_point_x,
                top_left_point_y,
                for_position=[self.position_x, self.position_y],
            ),
            GridPoint(
                self.numerical_step_size,
                top_left_point_x + 1,
                top_left_point_y,
                for_position=[self.position_x, self.position_y],
            ),
            GridPoint(
                self.numerical_step_size,
                top_left_point_x + 1,
                top_left_point_y + 1,
                for_position=[self.position_x, self.position_y],
            ),
            GridPoint(
                self.numerical_step_size,
                top_left_point_x,
                top_left_point_y + 1,
                for_position=[self.position_x, self.position_y],
            ),
        ]
        self.set_distance_to_points([self.position_x, self.position_y])
        self.set_influence_rate_to_points()
        return self.grid_points

    def get_nearest_grid_point(self):
        nearest_grid_point = self.grid_points[0]

        for grid_point in self.grid_points[1:]:
            if grid_point.distance < nearest_grid_point.distance:
                nearest_grid_point = grid_point

        return nearest_grid_point


class GridPointsForPath:
    def __init__(
        self, start_position: list, direction: Decimal, settings: Settings
    ) -> None:
        [self.start_position_x, self.start_position_y] = start_position
        self.direction = direction
        self.step_length = settings.STEP_LENGTH
        self.number_of_positions = settings.PHEROMONE_POINTS_IN_STEP
        self.numerical_step_size = settings.NUMERICAL_STEP_SIZE

        self.grid_points: List[GridPointsForPosition] = []

        self.get_positions_on_path()

    def get_positions_on_path(self):
        points_distance = self.step_length / self.number_of_positions
        delta_x = Decimal(math.cos(self.direction)) * points_distance
        delta_y = Decimal(math.sin(self.direction)) * points_distance
        current_position = np.array(
            [self.start_position_x, self.start_position_y]
        ) + np.array([delta_x, delta_y])

        for _ in range(self.number_of_positions):
            self.grid_points.append(
                GridPointsForPosition(self.numerical_step_size, current_position)
            )
            self.number_of_positions += 1

            current_position += np.array([delta_x, delta_y])


class GaussianTemplate:
    def __init__(self, settings):
        self.step_size = settings.STEP_LENGTH
        self.numerical_step_size = settings.NUMERICAL_STEP_SIZE
        self.numerical_array_size = settings.NUMERICAL_ARRAY_SIZE

        self.sigma = Decimal(settings.PHEROMONE_GAUSS_SIGMA)
        self.max_distance = Decimal(4 * self.sigma)

        self.sigma_num = self.sigma / self.numerical_step_size
        self.max_distance_num = Decimal(4 * self.sigma) / self.numerical_step_size

        # Grid points, not positions
        self.template = None
        self.start_x = 0
        self.start_y = 0
        self.center_x = None
        self.center_y = None
        self.end_x = None
        self.end_y = None

        self.set_template()

    def get_gaussian_radius(self, real_radius):
        if real_radius % self.numerical_step_size == 0:
            return real_radius / self.numerical_step_size
        grid_radius = math.ceil(real_radius)
        # necessary if the step is greater than 1
        while (grid_radius % self.numerical_step_size) != 0:
            grid_radius += 1
        while (grid_radius - real_radius) > self.numerical_step_size:
            grid_radius -= self.numerical_step_size
        return grid_radius / self.numerical_step_size

    def set_template(self):
        radius = self.get_gaussian_radius(self.max_distance_num)
        center = [radius, radius]
        size = int(2 * radius + 1)

        distances = np.zeros((size, size), dtype=Decimal)
        gaussian_values = np.zeros((size, size), dtype=Decimal)
        for i in range(size):
            for j in range(size):
                distance = get_point_distance(
                    self.numerical_step_size * np.array(center),
                    self.numerical_step_size * np.array([i, j], dtype=Decimal),
                )
                distances[i][j] = distance
                if distance <= self.max_distance:
                    gaussian_values[i][j] = Decimal(
                        stats.norm.pdf(
                            float(distance), loc=0.0, scale=float(self.sigma)
                        )
                    )

        self.template = gaussian_values / np.sum(gaussian_values)


class Gaussian:
    def __init__(self, gaussian_template: GaussianTemplate, grid_point: GridPoint):
        self.center = grid_point
        self.template = None
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None

        self.apply_template(gaussian_template)

    def normalize_template(self, numerical_array_size):
        if self.start_y < 0:
            self.template = self.template[:, abs(self.start_y) :]
            self.start_y = 0
        if self.end_y > numerical_array_size - 1:
            diff = self.end_y - numerical_array_size + 1
            self.template = self.template[:, :-diff]
            self.end_y -= diff

        if self.start_x < 0:
            self.template = self.template[abs(self.start_x) :, :]
            self.start_x = 0
        if self.end_x > numerical_array_size - 1:
            diff = self.end_x - numerical_array_size + 1
            self.template = self.template[:-diff, :]
            self.end_x -= diff

        if self.template.shape[0] == 0 or self.template.shape[1] == 0:
            self.template = None

    def apply_template(self, gaussian_template: GaussianTemplate):
        radius = int((gaussian_template.template.shape[0] - 1) / 2)
        self.start_x = self.center.x - radius
        self.start_y = self.center.y - radius
        self.end_x = self.center.x + radius
        self.end_y = self.center.y + radius
        self.template = self.center.amount * gaussian_template.template
        self.normalize_template(gaussian_template.numerical_array_size)


class PheromoneGaussians:
    def __init__(
        self,
        start_position: list,
        direction: Decimal,
        settings: Settings,
        total_amount: Decimal,
        gaussian_template: GaussianTemplate,
    ):
        [self.start_position_x, self.start_position_y] = start_position
        self.direction = direction
        self.step_length = settings.STEP_LENGTH
        self.number_of_positions = settings.PHEROMONE_POINTS_IN_STEP
        self.numerical_step_size = settings.NUMERICAL_STEP_SIZE

        self.positions = []
        self.total_amount = total_amount
        self.position_amount = total_amount / self.number_of_positions
        self.gaussians = []
        self.gaussian_template = gaussian_template

        self.get_positions()
        self.get_gaussians()

    def get_positions_on_segment(self):
        points_distance = self.step_length / self.number_of_positions
        delta_x = Decimal(math.cos(self.direction)) * points_distance
        delta_y = Decimal(math.sin(self.direction)) * points_distance
        current_position = np.array(
            [self.start_position_x, self.start_position_y]
        ) + np.array([delta_x, delta_y])
        for i in range(self.number_of_positions):
            self.positions.append(np.copy(current_position))
            current_position += np.array([delta_x, delta_y])

    def get_positions(self):
        if self.direction is not None:
            self.get_positions_on_segment()
        else:
            self.positions.append(
                np.array([self.start_position_x, self.start_position_y])
            )
            self.position_amount = self.total_amount / Decimal(5)

    def get_gaussians(self):
        for [position_x, position_y] in self.positions:
            grid_points = GridPointsForPosition(
                self.numerical_step_size, [position_x, position_y]
            ).grid_points
            for grid_point in grid_points:
                grid_point.set_amount_due_to_influence_rate(self.position_amount)
                self.gaussians.append(Gaussian(self.gaussian_template, grid_point))
