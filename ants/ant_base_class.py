import math
from decimal import Decimal

from environment import FoodSources, Nest
from pheromones import Pheromones
from settings import Settings, PheromoneReleaseType


class DetectedPheromones:
    def __init__(self) -> None:
        self.left_antennae = Decimal(0)
        self.left_antennae_normalized = Decimal(0)
        self.right_antennae = Decimal(0)
        self.right_antennae_normalized = Decimal(0)


class AntBaseClass:
    """
    This is the basic class for ant.
    Contains basic methods.
    During implementation, it is necessary to define the get_next_position method.
    """

    def __init__(
        self,
        settings: Settings,
        name: int,
        initial_position_x: Decimal,
        initial_position_y: Decimal,
        initial_direction: Decimal,
        looking_for_food: bool = True,
        pheromone_deposit_limit: int = None,
        is_recruiter: bool = False,
        created_at_step: int = 0,
    ):
        self.settings = settings
        self.name = str(name)
        self.created_at_step = created_at_step

        # TODO: replace usage with history or delete history
        self.previous_position_x = Decimal(initial_position_x)
        self.previous_position_y = Decimal(initial_position_y)

        self.current_position_x = Decimal(initial_position_x)
        self.current_position_y = Decimal(initial_position_y)
        self.current_direction = Decimal(initial_direction)
        self.current_detected_pheromones = DetectedPheromones()

        self.position_x_history = [initial_position_x]
        self.position_y_history = [initial_position_y]

        # Boolean
        self.looking_for_food = looking_for_food
        # FoodSource, food that the ant has found and is heading with it to the nest
        self.found_food = None

        # for every step: None or food id
        self.found_food_in_steps = [None] * (created_at_step + 1)
        # for every step: Boolean
        self.found_nest_in_steps = [False] * (created_at_step + 1)
        # for every step: number of recruited ants (if the ant is a recruiter)
        self.recruited_ants_in_steps = []

        self.is_recruiter = is_recruiter
        self.examine_food_in_steps = 0
        self.recruit_ants_number = 0

        if pheromone_deposit_limit is None:
            self.pheromone_deposit_limit = settings.PHEROMONE_DEPOSIT_LIMIT
        else:
            self.pheromone_deposit_limit = Decimal(pheromone_deposit_limit)

    def __str__(self):
        return (
            "Ant "
            + str(self.name)
            + " at position ["
            + str(self.current_position_x)
            + " , "
            + str(self.current_position_y)
            + "] with direction "
            + str(self.current_direction)
            + " ."
        )

    def get_current_ant_data(self):
        return {
            "x": str(self.current_position_x),
            "y": str(self.current_position_y),
            "previous_x": str(self.previous_position_x),
            "previous_y": str(self.previous_position_y),
            "direction": str(self.current_direction),
            "looking_for_food": self.looking_for_food,
            "pheromone_deposit_limit": str(self.pheromone_deposit_limit),
            "is_recruiter": str(self.is_recruiter),
            "recruit_ants_number": self.recruit_ants_number,
        }

    def get_ant_final_results(self):
        return {
            "name": str(self.name),
            "created_at_step": str(self.created_at_step),
            "x": str(self.current_position_x),
            "y": str(self.current_position_y),
            "previous_x": str(self.previous_position_x),
            "previous_y": str(self.previous_position_y),
            "direction": str(self.current_direction),
            "looking_for_food": self.looking_for_food,
            "pheromone_deposit_limit": str(self.pheromone_deposit_limit),
            "found_food_in_steps": self.found_food_in_steps,
            "found_nest_in_steps": self.found_nest_in_steps,
            "is_recruiter": str(self.is_recruiter),
            "examine_food_in_steps": self.examine_food_in_steps,
            "recruit_ants_number": self.recruit_ants_number,
        }

        # 'position_x_history': self.position_x_history, 'position_y_history': self.position_y_history}

    def get_previous_position(self):
        return [self.previous_position_x, self.previous_position_y]

    def get_current_position(self):
        return [self.current_position_x, self.current_position_y]

    @staticmethod
    def get_position_in_direction(position: list, direction: Decimal, step: int):
        next_position_x = position[0] + (Decimal(math.cos(direction)) * step)
        next_position_y = position[1] + (Decimal(math.sin(direction)) * step)
        return [next_position_x, next_position_y]

    def get_left_antennae_position(self):
        diff_x = self.settings.ANTENNAE_LENGTH * Decimal(
            math.cos(self.current_direction + self.settings.LEFT_ANTENNAE_ANGLE)
        )
        diff_y = self.settings.ANTENNAE_LENGTH * Decimal(
            math.sin(self.current_direction + self.settings.LEFT_ANTENNAE_ANGLE)
        )
        return [self.current_position_x + diff_x, self.current_position_y + diff_y]

    def get_right_antennae_position(self):
        diff_x = self.settings.ANTENNAE_LENGTH * Decimal(
            math.cos(self.current_direction - self.settings.RIGHT_ANTENNAE_ANGLE)
        )
        diff_y = self.settings.ANTENNAE_LENGTH * Decimal(
            math.sin(self.current_direction - self.settings.RIGHT_ANTENNAE_ANGLE)
        )
        return [self.current_position_x + diff_x, self.current_position_y + diff_y]

    def get_amount_of_pheromone_for_deposition(self):
        if self.looking_for_food:
            return self.settings.AMOUNT_OF_PHEROMONE_NEST_MARK
        else:
            # TODO: move 0.75 to constant
            return self.settings.AMOUNT_OF_PHEROMONE_FOOD_MARK * (
                self.found_food.quality
                if self.settings.AFFECT_PHEROMONE_AMOUNT
                else Decimal(0.75)
            )

    def is_position_relevant(self, position):
        x, y = position
        return (
            Decimal(0) <= x <= self.settings.ENVIRONMENT_SIZE
            and Decimal(0) <= y <= self.settings.ENVIRONMENT_SIZE
        )

    def is_road_relevant(self):
        return self.is_position_relevant(
            self.get_current_position()
        ) or self.is_position_relevant(self.get_previous_position())

    # if direction is None, pheromone will be released on position
    def get_position_and_direction_to_spread_pheromone(self):
        if (
            self.current_position_x == self.previous_position_x
            and self.current_position_y == self.previous_position_y
        ):
            return self.get_current_position(), None
        return self.get_previous_position(), self.current_direction

    def spread_pheromones(self, pheromones: Pheromones, type: PheromoneReleaseType):
        if self.pheromone_deposit_limit > 0:
            # do not spread pheromone, if ant is not in monitored area
            if self.is_road_relevant():
                (
                    position,
                    direction,
                ) = self.get_position_and_direction_to_spread_pheromone()
                amount = self.get_amount_of_pheromone_for_deposition()

                if type == PheromoneReleaseType.GAUSSIAN:
                    pheromones.add_pheromone_to_road(
                        position, direction, self.looking_for_food, amount=amount
                    )
                elif type == PheromoneReleaseType.POSITION:
                    pheromones.add_pheromone_to_position(
                        position, direction, self.looking_for_food, amount=amount
                    )
                elif type == PheromoneReleaseType.NEAREST_GRID_POINT:
                    pheromones.add_pheromone_to_nearest_grid_point(
                        position, direction, self.looking_for_food, amount=amount
                    )
                else:
                    raise NotImplementedError(
                        'Unknown pheromone release type "' + str(type) + '".'
                    )
            self.pheromone_deposit_limit -= 1

    def normalize_pheromone_value(self, pheromone_value: Decimal):
        if pheromone_value < self.settings.MINIMUM_DETECTABLE_PHEROMONE:
            return Decimal("0.0")
        return pheromone_value

    def set_detected_pheromones(self, pheromones: Pheromones):
        left_position = self.get_left_antennae_position()
        left_pheromone = pheromones.get_watched_pheromone_value(
            left_position, self.looking_for_food
        )

        right_position = self.get_right_antennae_position()
        righ_pheromone = pheromones.get_watched_pheromone_value(
            right_position, self.looking_for_food
        )

        self.current_detected_pheromones.left_antennae = left_pheromone
        self.current_detected_pheromones.left_antennae_normalized = (
            self.normalize_pheromone_value(left_pheromone)
        )
        self.current_detected_pheromones.right_antennae = righ_pheromone
        self.current_detected_pheromones.right_antennae_normalized = (
            self.normalize_pheromone_value(righ_pheromone)
        )

    def deterministic_move(self):
        c_left = self.current_detected_pheromones.left_antennae_normalized
        c_right = self.current_detected_pheromones.right_antennae_normalized

        if c_left == c_right:
            return Decimal(0)

        gama = Decimal(c_left - c_right).copy_abs() / (c_left + c_right)

        if gama <= self.settings.WEBER_LAW_THRESHOLD:
            return Decimal(0)
        if c_left > c_right:
            return Decimal(math.pi / 6)
        if c_left < c_right:
            return Decimal(-math.pi / 6)
        return Decimal(0)

    def stochastic_move(self, random_variable_value: Decimal):
        left_antennae_pheromone = (
            self.current_detected_pheromones.left_antennae_normalized
        )
        right_antennae_pheromone = (
            self.current_detected_pheromones.right_antennae_normalized
        )

        c_max = max(left_antennae_pheromone, right_antennae_pheromone)
        if c_max == 0:
            k = Decimal(1.0)
        else:
            k = min(
                Decimal(1.0),
                max(
                    self.settings.MIN_K_VALUE, self.settings.PHEROMONE_C_MINIMUM / c_max
                ),
            )
        return (
            k
            * Decimal(random_variable_value)
            * (self.settings.STANDARD_DEVIATION_OF_RANDOM_CHANGE ** Decimal("2"))
        )

    def get_next_position(self, pheromones, random_variable_value):
        raise NotImplementedError

    @staticmethod
    def normalize_ant_direction(direction: Decimal):
        while direction > Decimal(2 * math.pi):
            direction -= Decimal(2 * math.pi)
        while direction < 0:
            direction += Decimal(2 * math.pi)
        return direction

    def turn_around(self):
        if self.current_direction > Decimal(math.pi):
            self.current_direction = self.normalize_ant_direction(
                self.current_direction - Decimal(math.pi)
            )
        else:
            self.current_direction = self.normalize_ant_direction(
                self.current_direction + Decimal(math.pi)
            )

    def move_with_direction(self, direction: Decimal, step: int):
        direction = self.normalize_ant_direction(direction)
        next_position = self.get_position_in_direction(
            self.get_current_position(), direction, step
        )
        return next_position

    def move(
        self,
        step: int,
        pheromones: Pheromones,
        foods: FoodSources,
        nest: Nest,
        random_variable_value: Decimal,
    ):
        if self.examine_food_in_steps > 0:
            self.examine_food_in_steps -= 1

            self.found_food_in_steps.append(None)
            self.found_nest_in_steps.append(False)

            self.previous_position_x, self.previous_position_y = (
                self.current_position_x,
                self.current_position_y,
            )

            return

        [next_position_x, next_position_y, next_direction] = self.get_next_position(
            pheromones, random_variable_value
        )

        self.previous_position_x, self.previous_position_y = (
            self.current_position_x,
            self.current_position_y,
        )
        self.current_position_x, self.current_position_y = (
            next_position_x,
            next_position_y,
        )
        self.current_direction = next_direction

        self.position_x_history.append(self.current_position_x)
        self.position_y_history.append(self.current_position_y)

        found_food = self.looking_for_food is True and foods.find_food(
            next_position_x, next_position_y, step
        )
        found_nest = self.looking_for_food is False and nest.found_nest(
            [next_position_x, next_position_y]
        )

        if found_food:
            self.looking_for_food = False
            self.pheromone_deposit_limit = self.settings.PHEROMONE_DEPOSIT_LIMIT
            self.turn_around()
            self.found_food = found_food

            if self.is_recruiter:
                self.examine_food_in_steps = self.settings.TIME_OF_FOOD_EXAMINATION

        if found_nest:
            nest.add_food(self.found_food.quality)
            self.looking_for_food = True
            self.pheromone_deposit_limit = self.settings.PHEROMONE_DEPOSIT_LIMIT
            self.turn_around()

            if self.is_recruiter:
                # TODO: move 0.75 to constant
                self.recruit_ants_number = int(
                    self.settings.MAX_RECRUITED_ANTS_AT_ONCE
                    * (
                        self.found_food.quality
                        if self.found_food.affect_recruitment
                        else Decimal("0.75")
                    )
                )
            self.found_food = None

        self.found_food_in_steps.append(found_food.id if found_food else None)
        self.found_nest_in_steps.append(found_nest)

        return
