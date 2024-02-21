from decimal import Decimal

from ants.ant_base_class import AntBaseClass
from pheromones import Pheromones


class AntWithPheromones(AntBaseClass):
    def get_next_position(self, pheromones: Pheromones, random_variable_value: Decimal):
        self.set_detected_pheromones(pheromones=pheromones)

        direction_change = self.deterministic_move() + self.stochastic_move(
            random_variable_value
        )
        direction_change = self.normalize_ant_direction(direction_change)
        next_direction = self.current_direction + direction_change
        [next_position_x, next_position_y] = self.move_with_direction(
            next_direction, self.settings.STEP_LENGTH
        )
        return [next_position_x, next_position_y, next_direction]
