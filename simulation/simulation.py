from save_results.draw_step import draw_step
from environment import FoodSources, Nest
from save_results import ResultsManager
from settings import Settings
from .threads_management import ThreadsManagement
from .time_measurement import TimeMeasurement
import numpy as np
from ants import AntsWithPheromones, AntsWithOrientation
from pheromones import Pheromones
from datetime import datetime
from helper_functions import try_make_dir


class Simulation:
    def __init__(
        self,
        number_of_steps: int = 10,
        settings: dict = None,
        random_variable_values: list = None,
        results_folder: str = None,
        simulation_folder_name: str = None,
        simulation_name: str = None,
        only_general_pheromone: bool = False,
        with_orientation: bool = False,
        save_pheromones_every_nth_step: int = 100,
    ):
        self.simulation_name = simulation_name

        self.current_step = 0
        self.to_step = number_of_steps
        self.time_measurement = TimeMeasurement()
        self.settings = Settings(settings)
        self.threads_management = ThreadsManagement()
        self.results_manager = ResultsManager(
            folder_name=simulation_folder_name,
            results_folder=results_folder,
            save_pheromones_every_nth_step=save_pheromones_every_nth_step,
        )

        self.random_variable_values = random_variable_values
        if self.random_variable_values is None:
            self.random_variable_values = np.random.normal(
                0, 1, self.settings.ANTS_NUMBER * number_of_steps
            ).tolist()

        if with_orientation:
            self.ants = AntsWithOrientation(self.settings, self.random_variable_values)
        else:
            self.ants = AntsWithPheromones(self.settings, self.random_variable_values)
        self.foods = FoodSources(self.settings)
        self.nest = Nest(self.settings)
        self.pheromones = Pheromones(
            self.settings,
            only_food_pheromone=with_orientation,
            only_general_pheromone=only_general_pheromone,
        )

        self.results_manager.create_directories()
        self.results_manager.save_settings(self.settings)
        self.results_manager.save_random_variable_values(self.random_variable_values)

    def get_results(self):
        summary = {
            "number_of_steps": self.to_step,
            "simulation_name": self.simulation_name,
            "ants": self.ants.get_ants_final_results(),
            "ants_stats": self.ants.get_ants_stats(),
            "foods": self.foods.get_food_data(),
            "nest": self.nest.get_nest_data(),
        }
        return summary

    def run_simulation(self):
        start = datetime.now()
        folder_name = self.results_manager.folder_name

        self.results_manager.save_step_in_thread(
            0, self.ants.get_current_ants_data(), self
        )
        self.current_step += 1

        while self.current_step <= self.to_step:
            ants_results = self.time_measurement.run_function(
                self.ants.move_all,
                self.current_step,
                self.pheromones,
                self.foods,
                self.nest,
            )
            self.time_measurement.run_function(
                self.ants.spread_pheromones, self.pheromones
            )

            for _ in range(self.settings.NUMBER_OF_DIFFUSIONS_IN_STEP):
                self.time_measurement.run_function(self.pheromones.diffuse)

            self.nest.add_food_supplies()

            self.results_manager.save_step_in_thread(
                self.current_step, ants_results, self
            )

            self.current_step += 1

        self.results_manager.save_final_results(self.get_results())
        self.threads_management.join()

        additional_times = {"calculation_duration": str(datetime.now() - start)}
        self.time_measurement.print_durations(folder_name, additional_times)
        self.time_measurement.save_durations_to_file(
            self.results_manager.results_folder, folder_name, additional_times
        )

    def draw_results(
        self,
        steps: list,
        additional_settings: dict = None,
        print_step_number: bool = False,
    ):
        try_make_dir(
            f"{self.results_manager.results_folder}/results/{self.results_manager.folder_name}/drawings"
        )

        if additional_settings is not None:
            self.settings.set_props(additional_settings)

        for step in steps:
            if print_step_number:
                print(self.results_manager.folder_name + ": Draw step " + str(step))
            draw_step(
                f"{self.results_manager.results_folder}/results/{self.results_manager.folder_name}",
                "drawings",
                step,
                self.settings,
            )
