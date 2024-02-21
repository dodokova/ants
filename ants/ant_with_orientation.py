import math
from decimal import Decimal

from ants.ant_base_class import AntBaseClass
from helper_functions import get_point_distance
from pheromones import Pheromones


class AntWithOrientation(AntBaseClass):
    def get_nest_center_position(self):
        return [self.settings.NEST_POSITION[0], self.settings.NEST_POSITION[1]]

    def get_distance_from_nest(self):
        return Decimal(
            get_point_distance(
                self.get_nest_center_position(),
                [self.current_position_x, self.current_position_y],
            )
        )

    def get_direction_to_nest(self):
        [nest_x, nest_y] = self.get_nest_center_position()
        arc_tan_value = Decimal(
            math.atan(
                (self.current_position_y - nest_y).copy_abs()
                / (self.current_position_x - nest_x).copy_abs()
            )
        )

        # case when the ant and the nest are "above each other"
        if nest_x == self.current_position_x:
            if nest_y > self.current_position_y:
                return Decimal(math.pi) / Decimal("2")
            elif nest_y < self.current_position_y:
                return Decimal(math.pi) / Decimal("-2")
            else:
                raise ValueError("Ant is in nest.")

        # case when the ant and the nest are "next to each other"
        if nest_y == self.current_position_y:
            if nest_x > self.current_position_x:
                return Decimal("0")
            elif nest_x < self.current_position_x:
                return Decimal(math.pi)
            else:
                raise ValueError("Ant is in nest.")

        if nest_x > self.current_position_x:
            absolute_angle = arc_tan_value
        else:
            absolute_angle = Decimal(math.pi) - arc_tan_value

        if nest_y > self.current_position_y:
            return absolute_angle
        else:
            return absolute_angle * Decimal("-1")

    def get_next_position(self, pheromones: Pheromones, random_variable_value: Decimal):
        self.set_detected_pheromones(pheromones=pheromones)

        if self.looking_for_food:
            direction_change = self.deterministic_move() + self.stochastic_move(
                random_variable_value
            )
            next_direction = self.current_direction + direction_change
            [next_position_x, next_position_y] = self.move_with_direction(
                next_direction, self.settings.STEP_LENGTH
            )
            return [next_position_x, next_position_y, next_direction]

        else:
            distance_from_nest = self.get_distance_from_nest()
            next_direction = self.get_direction_to_nest() + (
                min(
                    Decimal(1),
                    self.settings.ORIENTATION_RANDOMNESS * distance_from_nest,
                )
                * Decimal(random_variable_value)
            )
            [next_position_x, next_position_y] = self.move_with_direction(
                next_direction, self.settings.STEP_LENGTH
            )
            return [next_position_x, next_position_y, next_direction]
