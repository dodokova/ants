import json
import os
from datetime import datetime

from settings import Settings


class ResultsManager:
    def __init__(
        self, results_folder="", folder_name=None, save_pheromones_every_nth_step=100
    ):
        self.results_folder = results_folder
        self.folder_name = folder_name or str(datetime.now())
        self.save_pheromones_every_nth_step = save_pheromones_every_nth_step

    def create_directories(self):
        os.mkdir(f"{self.results_folder}/results/{self.folder_name}")
        os.mkdir(f"{self.results_folder}/results/{self.folder_name}/data")

    def save_settings(self, settings: Settings):
        with open(
            f"{self.results_folder}/results/{self.folder_name}/settings.py", "w"
        ) as new_settings_file:
            data = settings.to_dict()
            new_settings_file.write(json.dumps(data))

    def save_random_variable_values(self, random_variable_values: list):
        with open(
            f"{self.results_folder}/results/{self.folder_name}/random_variable.py", "w"
        ) as file:
            file.write(str(random_variable_values))

    def save_step_results_file(self, step: int, results: dict):
        with open(
            f"{self.results_folder}/results/{self.folder_name}/data/{step:05d}.txt", "w"
        ) as file:
            json.dump(results, file)

    def save_step_in_thread(self, step: int, ants_data: dict, simulation):
        summary = {
            "step": step,
            "ants": ants_data,
            "foods": simulation.foods.get_food_data(),
            "nest": simulation.nest.get_nest_data(),
        }
        if (simulation.current_step % self.save_pheromones_every_nth_step) == 0:
            summary.update(simulation.pheromones.get_pheromones_str_data())
        simulation.threads_management.add_and_start(
            target=self.save_step_results_file, args=(step, summary)
        )

    def save_final_results(self, results: dict):
        with open(
            f"{self.results_folder}/results/{self.folder_name}/data/results.txt", "w"
        ) as file:
            json.dump(results, file)
