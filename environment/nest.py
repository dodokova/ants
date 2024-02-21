from helper_functions import get_point_distance
from settings import Settings


class Nest:
    def __init__(self, settings: Settings):
        self.x = settings.NEST_POSITION[0]
        self.y = settings.NEST_POSITION[1]
        self.radius = settings.NEST_POSITION[2]
        self.food_supplies_in_steps = [0]
        self.food_satisfaction_in_steps = [0.0]
        self.food_supplies_in_current_step = 0
        self.food_satisfaction_in_current_step = 0.0

    def get_nest_data(self):
        return {
            "x": str(self.x),
            "y": str(self.y),
            "radius": str(self.radius),
            "food_supplies_in_steps": self.food_supplies_in_steps,
            "food_satisfaction_in_steps": self.food_satisfaction_in_steps,
        }

    def add_food_supplies(self):
        self.food_supplies_in_steps.append(
            self.food_supplies_in_steps[-1] + self.food_supplies_in_current_step
        )
        self.food_satisfaction_in_steps.append(
            self.food_satisfaction_in_steps[-1] + self.food_satisfaction_in_current_step
        )
        self.food_supplies_in_current_step = 0
        self.food_satisfaction_in_current_step = 0.0

    def add_food(self, food_quality):
        self.food_supplies_in_current_step += 1
        self.food_satisfaction_in_current_step += float(food_quality)

    def found_nest(self, ant_position: list):
        return get_point_distance(ant_position, [self.x, self.y]) <= self.radius
