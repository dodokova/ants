from decimal import Decimal
import numpy as np

from settings import Settings
from .grid_points import (
    Gaussian,
    PheromoneGaussians,
    GridPointsForPosition,
    GridPoint,
    GridPointsForPath,
)


class Pheromone:
    def __init__(
        self,
        settings: Settings,
        pde_decay: Decimal,
        diffusion_constant: Decimal,
        current_field=None,
    ):
        self.size = settings.NUMERICAL_ARRAY_SIZE
        self.settings = settings
        self.current_field = (
            current_field
            if current_field is not None
            else self._generate_pheromone_field(settings.NUMERICAL_ARRAY_SIZE)
        )

        self.diffusion_constant = diffusion_constant
        self.pde_decay = pde_decay
        self.decay_multiplicator = Decimal("1") - (
            self.settings.DIFFUSION_DELTA_T * self.pde_decay
        )
        self.multiplicator = (
            self.diffusion_constant
            * self.settings.DIFFUSION_DELTA_T
            / (self.settings.NUMERICAL_STEP_SIZE ** Decimal("2"))
        )

        self.gaussian_template = None

    def set_gaussian_template(self, template):
        self.gaussian_template = template

    @staticmethod
    def _generate_pheromone_field(size: int):
        return np.zeros((size, size), dtype=np.dtype(Decimal))

    def _get_pheromone_grid_point_value(self, i: int, j: int):
        if i < 0 or j < 0:
            return Decimal(0)
        try:
            return Decimal(self.current_field[i][j])
        except IndexError:
            return Decimal(0)

    def get_pheromone_grid_point(self, grid_point: GridPoint):
        return self._get_pheromone_grid_point_value(grid_point.x, grid_point.y)

    # position = real position [x, y], not grid
    def get_pheromone_value(self, position: list):
        pheromone_value = Decimal(0)
        for grid_point in GridPointsForPosition(
            self.settings.NUMERICAL_STEP_SIZE, position
        ).grid_points:
            pheromone_value += (
                grid_point.influence_rate * self.get_pheromone_grid_point(grid_point)
            )
        return pheromone_value

    def _add_pheromone_to_grid_point(self, x: int, y: int, value: Decimal):
        if x < 0 or y < 0:
            return
        try:
            self.current_field[x][y] = self.current_field[x][y] + Decimal(value)
        except IndexError:
            pass

    def add_pheromone_to_position(
        self, start_position: list, direction: Decimal, amount_of_pheromone: Decimal
    ):
        grid_points_for_path = GridPointsForPath(
            start_position=start_position, direction=direction, settings=self.settings
        )
        amount_of_pheromone_for_position = amount_of_pheromone / Decimal(
            grid_points_for_path.number_of_positions
        )

        for grid_points_for_position in grid_points_for_path.grid_points:
            for grid_point in grid_points_for_position.grid_points:
                self._add_pheromone_to_grid_point(
                    grid_point.x,
                    grid_point.y,
                    grid_point.influence_rate * amount_of_pheromone_for_position,
                )

    def add_pheromone_to_nearest_grid_point(
        self, start_position: list, direction: Decimal, amount_of_pheromone: Decimal
    ):
        grid_points_for_path = GridPointsForPath(
            start_position=start_position, direction=direction, settings=self.settings
        )
        amount_of_pheromone_for_position = amount_of_pheromone / Decimal(
            grid_points_for_path.number_of_positions
        )

        for grid_points_for_position in grid_points_for_path.grid_points:
            nearest_grid_point = grid_points_for_position.get_nearest_grid_point()
            self._add_pheromone_to_grid_point(
                nearest_grid_point.x,
                nearest_grid_point.y,
                amount_of_pheromone_for_position,
            )

    def _add_gaussian_to_pheromone_field(self, gaussian: Gaussian):
        if gaussian.template is None:
            return
        self.current_field[
            gaussian.start_x : gaussian.end_x + 1, gaussian.start_y : gaussian.end_y + 1
        ] += gaussian.template

    def add_pheromone_with_gaussian(
        self, start_position: list, direction: Decimal, amount_of_pheromone: Decimal
    ):
        pheromone_gaussians = PheromoneGaussians(
            start_position,
            direction,
            self.settings,
            amount_of_pheromone,
            self.gaussian_template,
        )
        for gaussian in pheromone_gaussians.gaussians:
            self._add_gaussian_to_pheromone_field(gaussian)

    def roll_current_field(self, direction=1, axis=0):
        new_matrix = np.roll(self.current_field, direction, axis=axis)
        if axis == 0:
            if direction == 1:
                new_matrix[0, :] = Decimal("0")
            else:
                new_matrix[-1, :] = Decimal("0")
        else:
            if direction == 1:
                new_matrix[:, 0] = Decimal("0")
            else:
                new_matrix[:, -1] = Decimal("0")
        return new_matrix

    def get_next_diffusion_step(self):
        return (
            self.decay_multiplicator - 4 * self.multiplicator
        ) * self.current_field + self.multiplicator * (
            self.roll_current_field(1, 0)
            + self.roll_current_field(-1, 0)
            + self.roll_current_field(1, 1)
            + self.roll_current_field(-1, 1)
        )

    def diffuse(self):
        self.current_field = self.get_next_diffusion_step()

    def get_pheromone_str_data(self):
        return np.round(np.array(self.current_field, dtype=float), 10).tolist()
