import json
import math
from decimal import Decimal


class PheromoneReleaseType:
    GAUSSIAN = "GAUSSIAN"
    POSITION = "POSITION"
    NEAREST_GRID_POINT = "NEAREST_GRID_POINT"


class Settings:
    def __init__(self, props={}):
        # ANT PARAMETERS
        self.BODY_LENGTH = Decimal("2.1")  # mm
        self.STEP_LENGTH = Decimal("2") * self.BODY_LENGTH  # -> one step is 0.5 second
        self.VELOCITY = Decimal("8.4")  # mm/s
        self.LEFT_ANTENNAE_ANGLE = Decimal(math.pi / 6)
        self.RIGHT_ANTENNAE_ANGLE = Decimal(math.pi / 6)
        self.ANTENNAE_LENGTH = Decimal(self.BODY_LENGTH / 3)
        self.WEBER_LAW_THRESHOLD = Decimal("0.005")
        # originally 1.0991
        self.STANDARD_DEVIATION_OF_RANDOM_CHANGE = Decimal(1)
        self.ORIENTATION_RANDOMNESS = Decimal(1 / 200)

        # SIMULATION PARAMETERS
        # number of ants at the beginning
        self.ANTS_NUMBER = 200
        # number of available ant (for recruitment) in nest
        self.AVAILABLE_ANTS = 100
        # ratio of recruiting ants at the beginning, from interval [0.00, 1.00], max two decimal places
        self.RECRUITMENT_RATIO = 1.0
        self.MAX_RECRUITED_ANTS_AT_ONCE = 6
        self.TIME_OF_FOOD_EXAMINATION = 30  # steps => x/2 seconds
        # originally 0.5
        self.NUMERICAL_STEP_SIZE = Decimal("1")  # grid size in mm
        self.ENVIRONMENT_SIZE = 300  # mm
        self.NUMERICAL_ARRAY_SIZE = (
            int(self.ENVIRONMENT_SIZE / self.NUMERICAL_STEP_SIZE) + 1
        )

        # PHEROMONES PARAMETERS
        self.DIFFUSION_CONSTANT_A = Decimal("0.05")  # mm^2/s
        self.DIFFUSION_CONSTANT_B = Decimal("0.05")

        self.PHEROMONE_DECAY_A = Decimal("10000")  # s
        self.PHEROMONE_DECAY_B = Decimal("500")  # s

        self.PDE_DECAY_PARAMETER_A = Decimal(
            "0.0002"
        )  # calculated from pheromone decay: 2/decay
        self.PDE_DECAY_PARAMETER_B = Decimal(
            "0.005"
        )  # calculated from pheromone decay: 2/decay

        self.AMOUNT_OF_PHEROMONE_FOOD_MARK = Decimal("0.03")  # g
        self.AMOUNT_OF_PHEROMONE_NEST_MARK = Decimal("0.02")  # g

        self.MINIMUM_DETECTABLE_PHEROMONE = Decimal("10") ** Decimal("-11")  # g

        self.PHEROMONE_C_MINIMUM = Decimal("0.005")  # g (for equation 1)

        self.PHEROMONE_GAUSS_SIGMA = Decimal("1.5")
        self.PHEROMONE_POINTS_IN_STEP = 4

        self.PHEROMONE_DEPOSIT_LIMIT = (
            int(self.VELOCITY / self.STEP_LENGTH) * 80
        )  # seconds
        # depends on stability condition
        self.DIFFUSION_DELTA_T = Decimal("0.5")
        self.NUMBER_OF_DIFFUSIONS_IN_STEP = int(
            self.STEP_LENGTH / self.VELOCITY / self.DIFFUSION_DELTA_T
        )
        self.PHEROMONE_RELEASE_TYPE = PheromoneReleaseType.GAUSSIAN

        # position: x, y, radius
        self.NEST_POSITION = [150, 150, 20]

        # position: x, y, radius, amount, quality, created_at (step), end_at (step or None)
        self.FOOD_SOURCES = [
            [65, 65, 15, 10000, 1, 0, None]
        ]  # distance from nest = 120mm
        # food quality affects number of recruited ants
        self.AFFECT_RECRUITMENT = True
        # food quality affects amount of pheromone emitted
        self.AFFECT_PHEROMONE_AMOUNT = True

        # PICTURES
        # picture size: (environment size * zoom) pixels
        self.ZOOM = 4
        # how many ant steps will be drawn in one picture
        self.NUMBER_OF_ANT_STEPS_IN_IMG = 10

        # TODO: consider usage
        self.MIN_K_VALUE = Decimal(0)

        # TODO: improve
        for key in list(props.keys()):
            self.__dict__[key] = self.get_string_to_required_type(
                props[key], self.__dict__[key]
            )
            if key == "ENVIRONMENT_SIZE" or key == "NUMERICAL_STEP_SIZE":
                self.NUMERICAL_ARRAY_SIZE = (
                    int(self.ENVIRONMENT_SIZE / self.NUMERICAL_STEP_SIZE) + 1
                )
            if key == "BODY_LENGTH":
                self.ANTENNAE_LENGTH = Decimal(self.BODY_LENGTH / 3)
            if key == "PHEROMONE_DECAY_A":
                self.PDE_DECAY_PARAMETER_A = Decimal("2") / self.PHEROMONE_DECAY_A
            if key == "PHEROMONE_DECAY_B":
                self.PDE_DECAY_PARAMETER_B = Decimal("2") / self.PHEROMONE_DECAY_B

    def to_dict(self):
        data_dict = self.__dict__.copy()
        for key in list(data_dict.keys()):
            data_dict[key] = (
                str(data_dict[key])
                if type(data_dict[key]) == Decimal
                else data_dict[key]
            )
        return data_dict

    def get_string_to_required_type(self, value, sample_value):
        if type(value) != str or type(sample_value) == str:
            return value
        value_type = type(sample_value)
        if value_type == Decimal:
            return Decimal(value)
        elif value_type == int:
            return int(value)
        elif value_type == float:
            return float(value)
        elif value_type == list:
            return [
                self.get_string_to_required_type(json.dumps(arr_part), arr_part)
                for arr_part in json.loads(value)
            ]
        return value

    def set_props(self, additional_settings: dict):
        for property_name, value in additional_settings.items():
            self.__dict__[property_name] = value
