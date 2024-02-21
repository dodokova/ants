from decimal import Decimal

from settings import Settings
from .grid_points import GaussianTemplate
from .pheromone import Pheromone


class Pheromones:
    def __init__(
        self,
        settings: Settings,
        only_food_pheromone: bool = False,
        only_general_pheromone: bool = False,
        pheromone_a=None,
        pheromone_b=None,
    ):
        self.settings = settings
        self.size = self.settings.NUMERICAL_ARRAY_SIZE
        self.only_food_pheromone = only_food_pheromone
        self.only_general_pheromone = only_general_pheromone

        gaussian_template = GaussianTemplate(settings)

        if only_food_pheromone and not only_general_pheromone:
            self.pheromone_a = None
        else:
            self.pheromone_a = Pheromone(
                self.settings,
                self.settings.PDE_DECAY_PARAMETER_A,
                self.settings.DIFFUSION_CONSTANT_A,
                current_field=pheromone_a,
            )
            self.pheromone_a.set_gaussian_template(gaussian_template)
        if only_general_pheromone:
            self.pheromone_b = None
        else:
            self.pheromone_b = Pheromone(
                self.settings,
                self.settings.PDE_DECAY_PARAMETER_B,
                self.settings.DIFFUSION_CONSTANT_B,
                current_field=pheromone_b,
            )
            self.pheromone_b.set_gaussian_template(gaussian_template)

    def get_released_pheromone(self, looking_for_food: bool):
        if self.only_general_pheromone:
            return self.pheromone_a
        elif looking_for_food:
            if self.only_food_pheromone:
                return None
            else:
                return self.pheromone_a
        else:
            return self.pheromone_b

    def get_watched_pheromone(self, looking_for_food: bool):
        if self.only_general_pheromone:
            return self.pheromone_a
        elif looking_for_food:
            return self.pheromone_b
        elif self.only_food_pheromone:
            return None
        else:
            return self.pheromone_a

    def get_watched_pheromone_value(self, position: list, looking_for_food: bool):
        pheromone = self.get_watched_pheromone(looking_for_food)
        if pheromone:
            return pheromone.get_pheromone_value(position)
        else:
            return Decimal(0)

    def add_pheromone_to_nearest_grid_point(
        self,
        start_position: list,
        direction: Decimal,
        looking_for_food: bool,
        amount: Decimal,
    ):
        if None in start_position or direction is None:
            return

        pheromone = self.get_released_pheromone(looking_for_food)
        if pheromone:
            pheromone.add_pheromone_to_nearest_grid_point(
                start_position, direction, amount
            )

    def add_pheromone_to_position(
        self,
        start_position: list,
        direction: Decimal,
        looking_for_food: bool,
        amount: Decimal,
    ):
        if None in start_position or direction is None:
            return

        pheromone = self.get_released_pheromone(looking_for_food)
        if pheromone:
            pheromone.add_pheromone_to_position(start_position, direction, amount)

    def add_pheromone_to_road(
        self,
        start_position: list,
        direction: Decimal,
        looking_for_food: bool,
        amount: Decimal,
    ):
        if None in start_position or direction is None:
            return

        pheromone = self.get_released_pheromone(looking_for_food)
        if pheromone:
            pheromone.add_pheromone_with_gaussian(start_position, direction, amount)

    def diffuse(self):
        if self.pheromone_a:
            self.pheromone_a.diffuse()
        if self.pheromone_b:
            self.pheromone_b.diffuse()

    def get_pheromones_str_data(self):
        data = {}
        if self.pheromone_a:
            data["pheromone_a"] = self.pheromone_a.get_pheromone_str_data()
        if self.pheromone_b:
            data["pheromone_b"] = self.pheromone_b.get_pheromone_str_data()
        return data
