import math
from decimal import *
import numpy as np
from ants.ant_with_orientation import AntWithOrientation
from ants.ant_with_pheromones import AntWithPheromones
from ants.ant_base_class import AntBaseClass, DetectedPheromones
from environment import FoodSources, Nest
from pheromones import Pheromones
from settings import Settings
from typing import Dict


class DetectedPheromonesStats:
    def __init__(self) -> None:
        self.both_antenae = []
        self.one_antennae = []
        self.no_antennae = []

    def add_new_step(self):
        self.both_antenae.append(0)
        self.one_antennae.append(0)
        self.no_antennae.append(0)

    def add_detected_pheromone(self, left_antennae: Decimal, right_antennae: Decimal):
        if left_antennae > 0 and right_antennae > 0:
            self.both_antenae[-1] += 1
        elif left_antennae > 0 or right_antennae > 0:
            self.one_antennae[-1] += 1
        else:
            self.no_antennae[-1] += 1

    def get_results(self):
        return {
            "both_antenae": self.both_antenae,
            "one_antennae": self.one_antennae,
            "no_antennae": self.no_antennae,
        }


class _Ants:
    """
    This is the basic class for ants.
    Contains basic methods.
    During implementation, it is necessary to define the create_ant method.
    """

    def __init__(
        self, settings: Settings, random_variable_values: list, ants: list = None
    ):
        self.settings = settings
        self.amount = settings.ANTS_NUMBER
        self.ants: Dict[str, AntBaseClass] = {}
        self.random_variable_values = random_variable_values or []
        self.available_ants = self.settings.AVAILABLE_ANTS
        self.current_step = 0
        self.detected_pheromones = {
            "real_value": DetectedPheromonesStats(),
            "normalized_value": DetectedPheromonesStats(),
        }

        if ants is None:
            self.create_initial_ants(settings)
        else:
            self.create_ants_from_data(settings, ants)

    def create_ant(
        self,
        settings: Settings,
        name: int,
        position_x: Decimal,
        position_y: Decimal,
        direction: Decimal,
        is_recruiter: bool = False,
        created_at_step: int = 0,
        looking_for_food=None,
        pheromone_deposit_limit=None,
    ):
        raise NotImplementedError

    def generate_division_of_recruiters(self):
        recruitment_ratio = self.settings.RECRUITMENT_RATIO
        arr = np.array([False] * self.amount)
        arr[: int(self.amount * recruitment_ratio)] = True
        np.random.shuffle(arr)
        return arr

    def create_initial_ants(self, settings: Settings):
        net_position_x = Decimal(settings.NEST_POSITION[0])
        net_position_y = Decimal(settings.NEST_POSITION[1])
        net_radius = Decimal(settings.NEST_POSITION[2])

        angle = Decimal(0)
        recruiters_arr = self.generate_division_of_recruiters()

        for i in range(self.amount):
            ant_position_x = net_position_x + (net_radius * Decimal(math.cos(angle)))
            ant_position_y = net_position_y + (net_radius * Decimal(math.sin(angle)))
            self.ants[str(i)] = self.create_ant(
                settings,
                i,
                ant_position_x,
                ant_position_y,
                angle,
                is_recruiter=recruiters_arr[i],
                created_at_step=0,
            )
            angle += Decimal(2 * math.pi / self.amount)

    # for analysis purpose only
    def create_ants_from_data(self, setting: Settings, ants):
        for ant_index, ant_data in enumerate(ants.values()):
            self.ants[ant_index] = self.create_ant(
                setting,
                ant_index,
                ant_data.get("x"),
                ant_data.get("y"),
                ant_data.get("direction"),
                is_recruiter=ant_data.get("is_recruiter"),
                created_at_step=0,
            )

    def get_current_ants_data(self):
        result = {}
        for ant in self.ants.values():
            result[ant.name] = ant.get_current_ant_data()
        return result

    def get_ants_final_results(self):
        results = {}
        for ant in self.ants.values():
            results[ant.name] = ant.get_ant_final_results()
        return results

    def get_ants_stats(self):
        return {
            "pheromones": {
                "real_values": self.detected_pheromones["real_value"].get_results(),
                "normalized_values": self.detected_pheromones[
                    "normalized_value"
                ].get_results(),
            }
        }

    def get_random_variable_value(self):
        try:
            return self.random_variable_values.pop()
        except IndexError:
            self.random_variable_values = np.random.normal(
                0, 1, self.settings.ANTS_NUMBER * 300
            ).tolist()
            return self.random_variable_values.pop()

    def spread_pheromones(self, pheromones):
        for ant in self.ants.values():
            ant.spread_pheromones(pheromones, self.settings.PHEROMONE_RELEASE_TYPE)

    def save_detected_pheromones(self, ant: AntBaseClass):
        self.detected_pheromones["real_value"].add_detected_pheromone(
            ant.current_detected_pheromones.left_antennae,
            ant.current_detected_pheromones.right_antennae,
        )
        self.detected_pheromones["normalized_value"].add_detected_pheromone(
            ant.current_detected_pheromones.left_antennae_normalized,
            ant.current_detected_pheromones.right_antennae_normalized,
        )

    def move_all(
        self, step: int, pheromones: Pheromones, foods: FoodSources, nest: Nest
    ):
        results = {}

        self.detected_pheromones["real_value"].add_new_step()
        self.detected_pheromones["normalized_value"].add_new_step()

        for ant in self.ants.values():
            ant.move(step, pheromones, foods, nest, self.get_random_variable_value())
            self.save_detected_pheromones(ant)
            results[ant.name] = ant.get_current_ant_data()

        recruitment_result = self.recruit_new_ants()
        results.update(recruitment_result)

        self.current_step += 1

        return results

    def recruit_new_worker_for_ant(self, ant, new_ant_name: int):
        new_ant = self.create_ant(
            self.settings,
            new_ant_name,
            ant.current_position_x,
            ant.current_position_y,
            ant.current_direction,
            is_recruiter=False,
            looking_for_food=True,
            created_at_step=self.current_step,
        )
        return new_ant

    def recruit_new_ants(self):
        result = {}
        new_ants = {}
        if self.available_ants < 1:
            return result
        for ant in self.ants.values():
            if ant.recruit_ants_number == 0:
                continue

            new_ants_number = ant.recruit_ants_number
            if self.available_ants < 1:
                return result
            if self.available_ants < new_ants_number:
                new_ants_number = self.available_ants

            for ant_number in range(new_ants_number):
                new_ant = self.recruit_new_worker_for_ant(
                    ant, int(self.amount + ant_number)
                )
                new_ants[new_ant.name] = new_ant
                result[new_ant.name] = new_ant.get_current_ant_data()

            ant.recruit_ants_number = 0
            self.amount += new_ants_number
            self.available_ants -= new_ants_number

        self.ants.update(new_ants)
        return result


class AntsWithOrientation(_Ants):
    def create_ant(self, *args, **kwargs):
        return AntWithOrientation(*args, **kwargs)


class AntsWithPheromones(_Ants):
    def create_ant(self, *args, **kwargs):
        return AntWithPheromones(*args, **kwargs)
