from .simulation import Simulation, AntOrientationType
from .threads_management import ProcessesManagement
from save_results import draw_results
from datetime import datetime
import numpy as np
from typing import List
from helper_functions import try_make_dir


class SimulationHandler:
    def __init__(
        self,
        results_folder: str,
        props: dict,
        simulation_folder_name: str,
        simulation_name: str,
        number_of_steps: int,
        random_variable_values=None,
        ant_orientation_type=AntOrientationType.TWO_PHEROMONES,
    ):
        self.results_folder = results_folder
        self.props = props
        self.simulation_folder_name = simulation_folder_name
        self.simulation_name = simulation_name
        self.number_of_steps = number_of_steps
        self.random_variable_values = random_variable_values
        self.ant_orientation_type = ant_orientation_type

    def create_and_run_simulation(self):
        Simulation(
            number_of_steps=self.number_of_steps,
            settings=self.props,
            random_variable_values=self.random_variable_values,
            simulation_folder_name=self.simulation_folder_name,
            simulation_name=self.simulation_name,
            results_folder=self.results_folder,
            ant_orientation_type=self.ant_orientation_type,
        ).run_simulation()


class SimulationFromGroup:
    def __init__(
        self,
        props: dict,
        simulation_folder_name: str,
        simulation_name: str,
        only_general_pheromone=False,
        with_orientation=False,
    ):
        self.props = props
        self.simulation_folder_name = simulation_folder_name
        self.simulation_name = simulation_name
        self.only_general_pheromone = only_general_pheromone
        self.with_orientation = with_orientation


class SimulationGroup:
    def __init__(
        self,
        results_folder: str,
        group_props: dict,
        group_name: str,
        number_of_steps: int,
        repetitions=1,
        max_processes=3,
    ):
        self.results_folder = results_folder

        self.group_props = group_props
        self.group_name = group_name

        self.number_of_steps = number_of_steps
        self.random_variable_values = None

        self.simulation_group: List[SimulationFromGroup] = []
        self.simulations_to_run: List[SimulationHandler] = []

        self.repetitions = repetitions

        self.max_processes = max_processes

        self.create_folders()

    def create_folders(self):
        try_make_dir(f"{self.results_folder}/results/{self.group_name}")

        for i in range(1, self.repetitions + 1):
            try_make_dir(f"{self.results_folder}/results/{self.group_name}/{str(i)}")

    def generate_random_variable_values(self, ants_number=250):
        return np.random.normal(0, 1, ants_number * self.number_of_steps * 2).tolist()

    def add_simulation(
        self,
        props: dict,
        folder_name: str,
        simulation_name: str,
        only_general_pheromone=False,
        with_orientation=False,
    ):
        self.simulation_group.append(
            SimulationFromGroup(
                props,
                folder_name,
                simulation_name,
                only_general_pheromone=only_general_pheromone,
                with_orientation=with_orientation,
            )
        )

    def create_simulations_to_run(self):
        for i in range(1, self.repetitions + 1):
            random_variables = self.generate_random_variable_values()
            for simulation in self.simulation_group:
                simulation_props = self.group_props.copy()
                simulation_props.update(simulation.props)
                simulation_name = (
                    f"{self.group_name}/{str(i)}/{simulation.simulation_folder_name}"
                )

                self.simulations_to_run.append(
                    SimulationHandler(
                        self.results_folder,
                        simulation_props,
                        simulation_name,
                        simulation.simulation_name,
                        self.number_of_steps,
                        random_variables,
                        only_general_pheromone=simulation.only_general_pheromone,
                        with_orientation=simulation.with_orientation,
                    )
                )

    def run_drawing(self):
        print("Running drawing...")
        start_draw = datetime.now()
        processes = ProcessesManagement(max_processes=self.max_processes)

        for simulation_handler in self.simulations_to_run:
            processes.add_waiting(
                target=draw_results,
                args=(
                    simulation_handler.simulation_folder_name,
                    self.results_folder,
                    self.number_of_steps,
                ),
            )

        processes.run_all()

        print("\nDrawing duration:", datetime.now() - start_draw)

    def run_simulations(self, should_draw_results=True):
        print("Running simulations...")
        start_simulate = datetime.now()
        processes = ProcessesManagement(max_processes=self.max_processes)

        self.create_simulations_to_run()

        for simulation_handler in self.simulations_to_run:
            processes.add_waiting(target=simulation_handler.create_and_run_simulation)

        processes.run_all()

        print("\nSimulations duration:", datetime.now() - start_simulate)

        if should_draw_results is True:
            self.run_drawing()
